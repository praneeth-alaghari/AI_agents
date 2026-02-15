"""
myAgentAI - Standard API Response Helpers
==========================================
All endpoints return a consistent JSON structure:
  { "success": bool, "message": str, "data": any }
"""

from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard response envelope."""
    success: bool
    message: str
    data: Optional[Any] = None


def success_response(message: str, data: Any = None) -> dict:
    """Return a success-formatted response dict."""
    return APIResponse(success=True, message=message, data=data).model_dump()


def error_response(message: str, data: Any = None) -> dict:
    """Return an error-formatted response dict."""
    return APIResponse(success=False, message=message, data=data).model_dump()
