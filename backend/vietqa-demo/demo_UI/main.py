# import os
# import re
# import unicodedata
# from io import BytesIO
# import base64

# import fitz
# import cv2 as cv
# import numpy as np
# import requests
# import pdfplumber
# import hashlib
# from typing import Optional, List
# from pdfminer.pdfparser import PDFSyntaxError

# import openai
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from sklearn.metrics.pairwise import cosine_similarity
# from pydantic import BaseModel
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
# from minio import Minio
# from minio.error import S3Error
# from langdetect import detect, DetectorFactory
# import bcrypt
# DetectorFactory.seed = 0

# from vector_db import embed, QdrantProvider
# from database import users_collection

# from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
# from fastapi.middleware.cors import CORSMiddleware

# load_dotenv()

# MODEL_NAME = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
# model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

# # URL of pytesseract service
# EXTRACT_TEXTS_URL_PYTESSERACT = "http://pytesseract:8081/extract_texts"

# # initialize text splitter
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

# MINIO_BUCKET = QDRANT_COLLECTION = "fpt"

# # JWT config
# SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120

# # Minio config
# minio_client = Minio(
#     "minio:9000",
#     access_key=os.getenv("MINIO_ACCESS_KEY"),
#     secret_key=os.getenv("MINIO_SECRET_KEY"),
#     secure=False
# )

# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)
#     print(f"Bucket '{MINIO_BUCKET}' did not exist and was created.")

# # Qdrant config
# vectordb_provider = QdrantProvider()
# vectordb_provider.create_collection(QDRANT_COLLECTION)

# # OpenAI key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Initial fastapi app and add CORS middleware
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # pydantic models
# class UserCreate(BaseModel):
#     username: str
#     password: str
#     role: str   # "manager" or "base"

# class LoginRequest(BaseModel):
#     username: str
#     password: str
    
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#     role: str
    
# def get_password_hash(password):
#     return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Endpoint register
# @app.post("/register")
# async def register(user: UserCreate):
#     existing_user = await users_collection.find_one({"username": user.username})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")
#     hashed_password = get_password_hash(user.password)
#     new_user = {"username": user.username, "hashed_password": hashed_password, "role": user.role}
#     await users_collection.insert_one(new_user)
#     return {"msg": "Registration successful"}

# # Endpoint login, return JWT token
# @app.post("/login", response_model=Token)
# async def login(login_req: LoginRequest):
#     user = await users_collection.find_one({"username": login_req.username})
#     if not user or not verify_password(login_req.password, user["hashed_password"]):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
#     return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}



# # get current user from JWT token
# async def get_current_user(authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token payload")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     user = await users_collection.find_one({"username": username})
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user

# # --- Các hàm xử lý PDF & tích hợp QA ---
# def normalize_filename(filename: str) -> str:
#     base = os.path.basename(filename)
#     nfkd_form = unicodedata.normalize('NFKD', base)
#     ascii_str = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
#     ascii_str = ascii_str.replace(" ", "_")
#     return re.sub(r'[^\w\-.]', '', ascii_str)

# def check_and_upload_minio(uploaded_file: UploadFile):
        
#     normalized_filename = normalize_filename(uploaded_file.filename)
#     print(f"Uploading {uploaded_file.filename} as {normalized_filename} to MinIO bucket '{MINIO_BUCKET}'...")
#     try:
#         minio_client.stat_object(MINIO_BUCKET, normalized_filename)
#         print(f"File '{normalized_filename}' already exists in the bucket.")
#         response = minio_client.get_object(MINIO_BUCKET, normalized_filename)
#         file_bytes = response.read()
#         return file_bytes, False, normalized_filename
#     except S3Error as err:
#         if err.code == "NoSuchKey":
#             uploaded_file.file.seek(0)
#             file_bytes = uploaded_file.file.read()
#             file_size = len(file_bytes)
#             print(f"File size: {file_size}")
#             if file_size == 0:
#                 raise HTTPException(status_code=400, detail="Empty file, cannot upload.")
#             minio_client.put_object(
#                 MINIO_BUCKET,
#                 normalized_filename,
#                 BytesIO(file_bytes),
#                 file_size,
#                 content_type="application/pdf"
#             )
#             print(f"File '{normalized_filename}' successfully uploaded.")
#             return file_bytes, True, normalized_filename
#         else:
#             raise HTTPException(status_code=500, detail=f"File upload error: {err}")

# def create_semantic_chunks(sentences):
#     semantic_chunks = []
#     embeddings = model.encode(sentences, convert_to_numpy=True)
#     for i, sentence in enumerate(sentences):
#         if i == 0:
#             semantic_chunks.append([sentence])
#         else:
#             similarity_score = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
#             if similarity_score > 0.85:
#                 semantic_chunks[-1].append(sentence)
#             else:
#                 semantic_chunks.append([sentence])
#     return semantic_chunks

# def rotate_image_by_angle(image, angle):
#     (h, w) = image.shape[:2]
#     (cX, cY) = (w // 2, h // 2)
#     M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
#     cos = np.abs(M[0, 0])
#     sin = np.abs(M[0, 1])
#     nW = int((h * sin) + (w * cos))
#     nH = int((h * cos) + (w * sin))
#     M[0, 2] += (nW / 2) - cX
#     M[1, 2] += (nH / 2) - cY
#     return cv.warpAffine(image, M, (nW, nH), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)

# def is_vietnamese(text: str) -> bool:
#     try:
#         language = detect(text)
#         return language == "vi"
#     except Exception:
#         return False

# def process_pdf_and_store(pdf_bytes, pdf_file_name):
#     try:
#         doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#         for page_index in range(len(doc)):
#             page = doc[page_index]
#             images = page.get_images(full=True)
#             if images:
#                 for img in images:
#                     xref = img[0]
#                     base_image = doc.extract_image(xref)
#                     image_bytes = base_image["image"]
                    
#                     image_array = cv.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
#                     if page.rotation:
#                         image_array = rotate_image_by_angle(image_array, page.rotation)
                    
#                     success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
#                     if not success:
#                         continue
#                     jpeg_bytes = encoded_image.tobytes()
                    
#                     files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
#                     response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
#                     if response.status_code == 200:
#                         ocr_text = response.json().get("data")
#                         if not is_vietnamese(ocr_text):
#                             print(f"Detected language is not Vietnamese for {pdf_file_name}. Skipping.")
#                             continue
#                         split_text = text_splitter.split_text(ocr_text)
#                         vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)
#             else:
#                 pix = page.get_pixmap(dpi=500)
#                 image_bytes = pix.tobytes("jpg")
#                 image_array = cv.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv.IMREAD_COLOR)
                
#                 if page.rotation:
#                     image_array = rotate_image_by_angle(image_array, page.rotation)
                    
#                 success, encoded_image = cv.imencode(".jpg", image_array, [int(cv.IMWRITE_JPEG_QUALITY), 95])
#                 if not success:
#                     continue
#                 jpeg_bytes = encoded_image.tobytes()
#                 files = {"image": (pdf_file_name, jpeg_bytes, "image/jpeg")}
#                 response = requests.post(EXTRACT_TEXTS_URL_PYTESSERACT, files=files)
#                 if response.status_code == 200:
#                     ocr_text = response.json().get("data")
#                     print(f"Extracted text from {pdf_file_name}: {ocr_text}")
#                     if not is_vietnamese(ocr_text):
#                         print(f"Detected language is not Vietnamese for {pdf_file_name}. Skipping.")
#                         continue
#                     split_text = text_splitter.split_text(ocr_text)
#                     vectordb_provider.add_vectors_(QDRANT_COLLECTION, split_text, pdf_file_name)
#         return {"status": "success", "message": "All pages processed and uploaded to Qdrant."}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}
    
# pdf_cache = {}

# def get_pdf_cache_key(file_bytes: bytes, dpi: int) -> str:
#     return hashlib.sha256(file_bytes + str(dpi).encode()).hexdigest()

# def extract_all_pages_images_cached(file_bytes, dpi=150):
#     key = get_pdf_cache_key(file_bytes, dpi)
#     if key in pdf_cache:
#         return pdf_cache[key]
    
#     images = extract_all_pages_images(file_bytes, dpi=dpi)
#     pdf_cache[key] = images
#     return images

# def extract_all_pages_images(file_bytes, dpi=300):
#     try:
#         file_obj = BytesIO(file_bytes)
#         file_obj.seek(0)
#         with pdfplumber.open(file_obj) as pdf:
#             images = []
#             for page in pdf.pages:
#                 pil_image = page.to_image(resolution=dpi).original
#                 image_array = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
#                 images.append(image_array)
#             return images
#     except PDFSyntaxError:
#         raise HTTPException(status_code=400, detail="This file is not a valid PDF or it is corrupted.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error occurred while processing PDF: {e}")

# # --- Các hàm Chatbot QA ---
# class ChatRequest(BaseModel):
#     question: str

# def generate_answer_from_llm(query: str, context: str) -> str:
#     prompt = f"Question: {query}\nContext: {context}\nAnswer:"
#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a chatbot that only provides answers based on the information in the system. "
#                     "If there is not enough information, respond with 'I don't know.'"
#                 )
#             },
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=350
#     )
#     return response["choices"][0]["message"]["content"].strip() if response["choices"] else "No valid answer generated."

# def rag_flow(question: str) -> str:
#     search_results = vectordb_provider.search_vector(QDRANT_COLLECTION, embed(question))
#     if not search_results:
#         return "No relevant context found."
#     context = " ".join([result.payload.get("content", "") for result in search_results])
#     try:
#         answer = generate_answer_from_llm(question, context)
#         return answer if answer else "No valid answer generated."
#     except Exception as e:
#         return f"Error during answer generation: {str(e)}"


# @app.post("/upload")
# def upload_pdf(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
#     # check if manager can hadle file upload
#     if user["role"] != "manager":
#         raise HTTPException(status_code=403, detail="Permission denied. Only managers can upload PDF files.")
    
#     for file in files:
#         file_bytes, is_new, normalized_filename = check_and_upload_minio(file)
#         if file_bytes is None:
#             raise HTTPException(status_code=400, detail=f"Upload failed for {normalized_filename}.")
#         if is_new:
#             result = process_pdf_and_store(file_bytes, normalized_filename)
#             if result.get("status") != "success":
#                 raise HTTPException(status_code=500, detail=f"Processing failed for {normalized_filename}: {result.get('message')}")
    
#     return {"msg": "All files uploaded and processed successfully."}

# @app.post("/delete_files")
# def delete_files(file: UploadFile = File(...), user=Depends(get_current_user)):
#     if user["role"] != "manager":
#         raise HTTPException(status_code=403, detail="Permission denied. Only managers can delete PDF files.")
    
#     try:
#         normalized_filename = normalize_filename(file.filename)
#         minio_client.remove_object(MINIO_BUCKET, normalized_filename)
#         vectordb_provider.delete_vectors(QDRANT_COLLECTION, normalized_filename)
#     except S3Error as err:
#         if err.code == "NoSuchKey":
#             raise HTTPException(status_code=404, detail=f"File not found: {normalized_filename}")
#         else:
#             raise HTTPException(status_code=500, detail=f"Error occurred while deleting file: {err}")
    
#     return {"msg": "Files deleted successfully."}

# @app.get("/pdf")
# def list_pdfs(current_user=Depends(get_current_user)):
#     objects = minio_client.list_objects(MINIO_BUCKET)
#     files = [obj.object_name for obj in objects]
#     return {"files": files}


# @app.get("/pdf/view/{filename}")
# def view_pdf(filename: str, page: Optional[int] = None, dpi: int = 150, user=Depends(get_current_user)):
#     try:
#         response = minio_client.get_object(MINIO_BUCKET, filename)
#         file_bytes = response.read()
#         images = extract_all_pages_images_cached(file_bytes, dpi=dpi)
        
#         # Lazy loading
#         if page is not None:
#             if page < 0 or page >= len(images):
#                 raise HTTPException(status_code=400, detail="Invalid page number")
#             images = [images[page]]
        
#         images_base64 = []
#         for img in images:
#             success, buffer = cv.imencode('.jpg', img)
#             if not success:
#                 continue
#             img_base64 = base64.b64encode(buffer).decode('utf-8')
#             images_base64.append(img_base64)
            
#         return {"filename": filename, "images": images_base64}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=f"File not found: {filename}")

# @app.post("/chat")
# def chat_endpoint(chat_req: ChatRequest, user=Depends(get_current_user)):
#     answer = rag_flow(chat_req.question)
#     return {"answer": answer}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, pdf_routes, chat_routes

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router, prefix="/api/users")
app.include_router(pdf_routes.router, prefix="/api/pdf")
app.include_router(chat_routes.router, prefix="/api/chat")