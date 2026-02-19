"""
FastAPI application entry point for Data Chat Bot backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import db_router, chat_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend API for Data Chat Bot – talk to your PostgreSQL databases in natural language.",
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(db_router.router)
app.include_router(chat_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
