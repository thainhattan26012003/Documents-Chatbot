from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user
from chat import rag_flow  

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat_endpoint(chat_req: ChatRequest, user=Depends(get_current_user)):
    answer = rag_flow(chat_req.question)
    return {"answer": answer}
