import os
import re
import unicodedata
import cv2 as cv
import numpy as np
from io import BytesIO
import requests
from fastapi import HTTPException
from minio.error import S3Error
from pdf2image import convert_from_bytes
from langchain_text_splitters import RecursiveCharacterTextSplitter
from service_config import MINIO_BUCKET, QDRANT_COLLECTION, minio_client, vectordb_provider
from fastapi import HTTPException, UploadFile


text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
EXTRACT_TEXTS_URL_PYTESSERACT = "http://pytesseract:8081/extract_texts"

def normalize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    nfkd_form = unicodedata.normalize("NFKD", base)
    ascii_str = nfkd_form.encode("ASCII", "ignore").decode("ASCII")
    ascii_str = ascii_str.replace(" ", "_")
    return re.sub(r"[^\w\-.]", "", ascii_str)

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

def process_image(image_array, pdf_file_name, page_index):
    if image_array is None:
        raise ValueError(f"Can not decode pdf image page: {page_index+1}")
    
    # Encode image -> JPEG
    success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
    if not success:
        raise ValueError(f"Can not encode pdf image page: {page_index+1}")
    jpeg_bytes = encoded_image.tobytes()
    
    files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
    response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
    if response.status_code == 200:
        ocr_text = response.json().get("data")
        split_text = text_splitter.split_text(ocr_text)
        vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)

def process_pdf_and_store(pdf_bytes, pdf_file_name):

    try:
        images = convert_from_bytes(pdf_bytes, dpi=500)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting PDF to images: {e}")
    
    for page_index, pil_image in enumerate(images):
        image_array = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
        process_image(image_array, pdf_file_name, page_index)
    return {"status": "success", "message": "All pages processed and images stored."}
