import os
import re
import unicodedata
from io import BytesIO

import fitz
import cv2 as cv
import numpy as np
import requests
import streamlit as st
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError

import openai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

from vector_db import embed, QdrantProvider

load_dotenv()

MODEL_NAME = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

# OCR service URLs
EXTRACT_TEXTS_URL_PYTESSERACT = "http://pytesseract:8081/extract_texts"

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

# MinIO Configuration
MINIO_BUCKET = "fpt"
minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

# Qdrant Configuration
QDRANT_COLLECTION = 'fpt'
vectordb_provider = QdrantProvider()
vectordb_provider.create_collection(QDRANT_COLLECTION)

# OpenAI Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

def normalize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    nfkd_form = unicodedata.normalize('NFKD', base)
    ascii_str = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    # Replace spaces with underscores
    ascii_str = ascii_str.replace(" ", "_")
    return re.sub(r'[^\w\-.]', '', ascii_str)

def get_base_name(filename: str) -> str:
    return os.path.splitext(filename)[0]

def is_probably_pdf(file_bytes: bytes) -> bool:
    return file_bytes.startswith(b"%PDF-")


def check_and_upload_minio(uploaded_file):
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
        st.write(f"Bucket '{MINIO_BUCKET}' did not exist and was created.")
    
    normalized_filename = normalize_filename(uploaded_file.name)
    st.write(f"Uploading {uploaded_file.name} as {normalized_filename} to MinIO bucket '{MINIO_BUCKET}'...")
    try:
        # check if file already exists in the bucket
        minio_client.stat_object(MINIO_BUCKET, normalized_filename)
        st.info(f"File '{normalized_filename}' already exists in the bucket.")
        response = minio_client.get_object(MINIO_BUCKET, normalized_filename)
        file_bytes = response.read()
        
        # If the file exists, we don't need to upload it again
        return file_bytes, False, uploaded_file.name
    except S3Error as err:
        if err.code == "NoSuchKey":
            uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            file_size = len(file_bytes)
            st.write(f"File size: {file_size}")
            if file_size == 0:
                st.error("Empty file, cannot upload.")
                return None, False
            minio_client.put_object(
                MINIO_BUCKET,
                normalized_filename,
                BytesIO(file_bytes),
                file_size,
                content_type="application/pdf"
            )
            st.success(f"File '{normalized_filename}' successfully uploaded.")
            return file_bytes, True, uploaded_file.name
        else:
            st.error(f"File upload error: {err}")
            return None, False, uploaded_file.name


def create_semantic_chunks(sentences):
    semantic_chunks = []
    embeddings = model.encode(sentences, convert_to_numpy=True)
    for i, sentence in enumerate(sentences):
        if i == 0:
            semantic_chunks.append([sentence])
        else:
            similarity_score = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
            if similarity_score > 0.85:  # Threshold can be adjusted
                semantic_chunks[-1].append(sentence)
            else:
                semantic_chunks.append([sentence])
    return semantic_chunks


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

def is_vietnamese(text: str) -> bool:
    try:
        language = detect(text)
        return language == "vi"
    except Exception as e:
        return False

def process_pdf_and_store(pdf_bytes, pdf_file_name):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in range(len(doc)):
            page = doc[page_index]
            images = page.get_images(full=True)
            if images:
                for img_idx, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image_array = cv.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
                    if page.rotation:
                        image_array = rotate_image_by_angle(image_array, page.rotation)
                    
                    success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
                    if not success:
                        continue
                    jpeg_bytes = encoded_image.tobytes()
                    
                    files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
                    response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
                    if response.status_code == 200:
                        ocr_text = response.json().get("data")
                        print(f"Extracted text from {pdf_file_name}: {ocr_text}")
                        if not is_vietnamese(ocr_text):
                            print(f"Detected language is not Vietnamese for {pdf_file_name}. Skipping.")
                            continue
                        split_text = text_splitter.split_text(ocr_text)
                        vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)
            else:
                # If there are no embedded images, rasterize the page
                pix = page.get_pixmap(dpi=500)
                image_bytes = pix.tobytes("jpg")
                image_array = cv.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
                
                if page.rotation:
                    image_array = rotate_image_by_angle(image_array, page.rotation)
                    
                success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
                if not success:
                    continue
                jpeg_bytes = encoded_image.tobytes()
                files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
                response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
                if response.status_code == 200:
                    ocr_text = response.json().get("data")
                    print(f"Extracted text from {pdf_file_name}: {ocr_text}")
                    if not is_vietnamese(ocr_text):
                            print(f"Detected language is not Vietnamese for {pdf_file_name}. Skipping.")
                            continue
                    split_text = text_splitter.split_text(ocr_text)
                    vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)
        return {"status": "success", "message": "All images have been processed and uploaded to Qdrant"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_all_pages_images(file_bytes, dpi=300):
    try:
        file_obj = BytesIO(file_bytes)
        file_obj.seek(0)
        with pdfplumber.open(file_obj) as pdf:
            return [page.to_image(resolution=dpi).original for page in pdf.pages]
    except PDFSyntaxError:
        st.error("This file is not a valid PDF or it is corrupted.")
        return []
    except Exception as e:
        st.error(f"Error occurred while processing PDF: {e}")
        return []

# QA with LLM 
class Question(BaseModel):
    question: str

def generate_answer_from_llm(query: str, context: str) -> str:
    prompt = f"Question: {query}\nContext: {context}\nAnswer:"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a chatbot that only provides answers based on the information you have learned "
                    "and data in the system. If there is not enough information, respond with 'I don't know.'"
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=350
    )
    return response["choices"][0]["message"]["content"].strip() if response["choices"] else "No valid answer generated."

def rag_flow(question: str) -> str:
    search_results = vectordb_provider.search_vector(QDRANT_COLLECTION, embed(question))
    if not search_results:
        return "No relevant context found."
    context = " ".join([result.payload.get("content", "") for result in search_results])
    try:
        answer = generate_answer_from_llm(question, context)
        return answer if answer else "No valid answer generated."
    except Exception as e:
        return f"Error during answer generation: {str(e)}"