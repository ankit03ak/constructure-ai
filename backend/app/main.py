from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .auth import router as auth_router
from .chat import router as chat_router

app = FastAPI(title="Constructure AI Email Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
