import os
import re
import unicodedata
import fitz
import cv2 as cv
import numpy as np
from io import BytesIO
import requests
from fastapi import HTTPException
from minio.error import S3Error
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import MINIO_BUCKET, IMAGE_MINIO_BUCKET, QDRANT_COLLECTION, minio_client, image_minio_client, vectordb_provider
from fastapi import HTTPException, UploadFile


text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
EXTRACT_TEXTS_URL_PYTESSERACT = "http://pytesseract:8081/extract_texts"

def normalize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    nfkd_form = unicodedata.normalize("NFKD", base)
    ascii_str = nfkd_form.encode("ASCII", "ignore").decode("ASCII")
    ascii_str = ascii_str.replace(" ", "_")
    return re.sub(r"[^\w\-.]", "", ascii_str)

def normalize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    nfkd_form = unicodedata.normalize('NFKD', base)
    ascii_str = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    ascii_str = ascii_str.replace(" ", "_")
    return re.sub(r'[^\w\-.]', '', ascii_str)

def rotate_image_by_angle(image, angle):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    return cv.warpAffine(image, M, (nW, nH), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)

def check_and_upload_minio(uploaded_file: UploadFile):
    normalized_filename = normalize_filename(uploaded_file.filename)
    print(f"Uploading {uploaded_file.filename} as {normalized_filename} to MinIO bucket '{MINIO_BUCKET}'...")
    try:
        minio_client.stat_object(MINIO_BUCKET, normalized_filename)
        print(f"File '{normalized_filename}' already exists in the bucket.")
        response = minio_client.get_object(MINIO_BUCKET, normalized_filename)
        file_bytes = response.read()
        return file_bytes, False, normalized_filename
    except S3Error as err:
        if err.code == "NoSuchKey":
            uploaded_file.file.seek(0)
            file_bytes = uploaded_file.file.read()
            if len(file_bytes) == 0:
                raise HTTPException(status_code=400, detail="Empty file, cannot upload.")
            minio_client.put_object(
                MINIO_BUCKET,
                normalized_filename,
                BytesIO(file_bytes),
                len(file_bytes),
                content_type="application/pdf"
            )
            print(f"File '{normalized_filename}' successfully uploaded.")
            return file_bytes, True, normalized_filename
        else:
            raise HTTPException(status_code=500, detail=f"File upload error: {err}")

def render_full_page(page, dpi=500):
    # Render full page image
    pix = page.get_pixmap(dpi=dpi)
    image_bytes = pix.tobytes("jpg")
    image_array = cv.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
    return image_array

def process_embedded_images(doc, page, pdf_file_name, page_index):
    images = page.get_images(full=True)
    for img in images:
        xref = img[0]
        base_image = doc.extract_image(xref)
        embedded_bytes = base_image.get("image")
        image_array = cv.imdecode(np.frombuffer(embedded_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
        yield image_array 


def process_image(image_array, pdf_file_name, page_index):
    if image_array is None:
        raise ValueError(f"Can not decode pdf image page: {page_index+1}")
    # Encode image -> JPEG
    success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
    if not success:
        raise ValueError(f"Can not encode pdf image page: {page_index+1}")
    jpeg_bytes = encoded_image.tobytes()
    
    # Save image in minio 
    image_filename = f"{pdf_file_name}_page{page_index+1}.jpg"
    image_stream = BytesIO(jpeg_bytes)
    file_size = len(jpeg_bytes)
    image_minio_client.put_object(
        IMAGE_MINIO_BUCKET,
        image_filename,
        image_stream,
        file_size,
        content_type="image/jpeg"
    )
    print(f"Image {image_filename} uploaded to minio.")
    
    files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
    response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
    if response.status_code == 200:
        ocr_text = response.json().get("data")
        split_text = text_splitter.split_text(ocr_text)
        vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)

def process_pdf_and_store(pdf_bytes, pdf_file_name):

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_index, page in enumerate(doc):

        rotation = page.rotation if page.rotation else 0
        
        # Render full page image
        full_page_image = render_full_page(page, dpi=500)
        if rotation:
            full_page_image = rotate_image_by_angle(full_page_image, rotation)
        process_image(full_page_image, pdf_file_name, page_index)  
        
        # Process embedded images
        for embedded_image in process_embedded_images(doc, page, pdf_file_name, page_index):
            if rotation:
                embedded_image = rotate_image_by_angle(embedded_image, rotation)
            process_image(embedded_image, pdf_file_name, page_index)  
    return {"status": "success", "message": "All pages processed and images stored."}

pdf_cache = {}
def get_pdf_cache_key(file_bytes: bytes, dpi: int) -> str:
    return hashlib.sha256(file_bytes + str(dpi).encode()).hexdigest()

def extract_all_pages_images_cached(file_bytes, dpi=150):
    key = get_pdf_cache_key(file_bytes, dpi)
    if key in pdf_cache:
        return pdf_cache[key]
    
    images = extract_all_pages_images(file_bytes, dpi=dpi)
    pdf_cache[key] = images
    return images

def extract_all_pages_images(file_bytes, dpi=300):
    try:
        file_obj = BytesIO(file_bytes)
        file_obj.seek(0)
        with pdfplumber.open(file_obj) as pdf:
            images = []
            for page in pdf.pages:
                pil_image = page.to_image(resolution=dpi).original
                image_array = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
                images.append(image_array)
            return images
    except PDFSyntaxError:
        raise HTTPException(status_code=400, detail="This file is not a valid PDF or it is corrupted.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while processing PDF: {e}")
