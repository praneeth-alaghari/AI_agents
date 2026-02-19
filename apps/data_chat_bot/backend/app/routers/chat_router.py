"""
Chat API router.
Endpoint for natural-language-to-SQL chat interaction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.text_to_sql import chat_with_data

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    db_name: str
    table_name: str


class ChatResponse(BaseModel):
    sql: str | None = None
    raw_results: dict | None = None
    summary: str


@router.post("/ask", response_model=ChatResponse)
def ask_question(req: ChatRequest):
    """Convert a natural-language question to SQL, execute it, and return a summary."""
    try:
        result = chat_with_data(req.question, req.db_name, req.table_name)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
