import os 
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["mydatabase"]

# user collection
users_collection = db["users"]

class UserCreate(BaseModel):
    username: str
    password: str
    role: str   # "manager" or "base"

class LoginRequest(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str