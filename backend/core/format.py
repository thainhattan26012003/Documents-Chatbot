import os
from dotenv import load_dotenv
from minio import Minio
from vector_db import QdrantProvider
from sentence_transformers import SentenceTransformer
load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

MINIO_BUCKET = QDRANT_COLLECTION = "law"

IMAGE_MINIO_BUCKET = "images"

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)
    
image_minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,
)

if not image_minio_client.bucket_exists(IMAGE_MINIO_BUCKET):
    image_minio_client.make_bucket(IMAGE_MINIO_BUCKET)

vectordb_provider = QdrantProvider()
vectordb_provider.create_collection(QDRANT_COLLECTION)

MODEL_NAME = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)