"""
myAgentAI - Standard Response Schema
======================================
Consistent JSON structure for all API endpoints.
"""

from pydantic import BaseModel
from typing import Any, Optional


class StandardResponse(BaseModel):
    """Every endpoint returns this envelope."""
    success: bool
    message: str
    data: Optional[Any] = None
