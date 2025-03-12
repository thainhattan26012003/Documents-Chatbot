import os
import uuid
import requests
from dotenv import load_dotenv
from qdrant_client.http import models
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient

load_dotenv('.env')

# Qdrant Client Setup
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), port=6333)

# URL Vietnamese Embeddor (FastAPI)
EMBEDDING_API_URL = "http://vietnamese-embed:8008/embed"

def embed(chunk):
    try:
        response = requests.post(EMBEDDING_API_URL, json={"texts": [chunk]})
        response.raise_for_status()  
        embeddings = response.json().get("embeddings", [])
        return embeddings[0] if embeddings else None
    except requests.exceptions.RequestException as e:
        print(f"? Error calling embedding API: {e}")
        return None

DEFAULT_DISTANCE = "Cosine"

class QdrantProvider:
    def __init__(self):
        # Initialize the QdrantProvider with a specific collection name
        test_embedidng = embed("test")
        self.vector_size = len(test_embedidng) if test_embedidng else 0 
        self.distance = DEFAULT_DISTANCE

    def create_collection(self, collection_name: str):
        # Check if the collection already exists
        if collection_name in self.list_collections():
            print(f"Collection `{collection_name}` already exists.")
            return

        # Create a new collection with the specified vector size and distance metric
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance[self.distance.upper()]
            )
        )
        print(f"Collection created `{collection_name}`")
        
    def list_collections(self):
        # List all existing collections in the Qdrant database
        collections = client.get_collections()
        return [col.name for col in collections.collections]
        
    def add_vectors_(self, collection_name: str, text, file_name):
        """Add multiple vectors to the client collection."""
        points = []

        for i, chunk in enumerate(text):
            vector = embed(chunk)
            
            point = PointStruct(
                id=str(uuid.uuid4()),  
                vector=vector,  
                payload={
                    "content": chunk, 
                    "file_name": file_name,
                }
            )
            points.append(point)
        client.upsert(collection_name=collection_name, points=points)
        print(f"{len(points)} Vectors added to `{collection_name}`")

    def search_vector(self, collection_name: str, vector: list[float], limit=5, with_payload=True):
        # Perform the search query in client with the provided parameters
        search_result = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,  # Limit the number of search results
            with_payload=with_payload,  # Whether to include payload in results
        )
        print(f"Vector searched `{collection_name}`")
        return search_result

        
