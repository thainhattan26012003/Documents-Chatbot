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