from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Initialize FastAPI
app = FastAPI(title="Vietnamese Document Embedding API")

# Load the Vietnamese document embedding model from Hugging Face.
# 'trust_remote_code=True' is needed because the model requires custom code execution.
model = SentenceTransformer('dangvantuan/vietnamese-document-embedding', trust_remote_code=True)

# Define the request body schema
class EmbedRequest(BaseModel):
    texts: list[str]


@app.post("/embed")
async def embed_text(request: EmbedRequest):
    embeddings = model.encode(request.texts).tolist()
    return {"embeddings": embeddings}
