from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import users_collection  
from auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta
import os

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

@router.post("/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    new_user = {"username": user.username, "hashed_password": hashed_password, "role": user.role}
    await users_collection.insert_one(new_user)
    return {"msg": "Registration successful"}

@router.post("/login", response_model=Token)
async def login(login_req: LoginRequest):
    user = await users_collection.find_one({"username": login_req.username})
    if not user or not verify_password(login_req.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120)))
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
