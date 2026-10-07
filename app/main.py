import os
import secrets

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from app.auth import router as auth_router
from app.chatbot import router as chatbot_router
from app.database import ensure_indexes

app = FastAPI(title="Travel RAG Assistant")

app.add_middleware(
    SessionMiddleware,
    # Set SESSION_SECRET for stable sessions. A safe local fallback avoids a
    # predictable hard-coded key during development.
    secret_key=os.getenv("SESSION_SECRET", secrets.token_urlsafe(32)),
)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth_router)
app.include_router(chatbot_router)


@app.on_event("startup")
def startup():
    # Do not load embeddings/FAISS here. Fast replies must work even while the
    # local RAG model is not loaded yet; the RAG engine initializes on demand.
    ensure_indexes()
