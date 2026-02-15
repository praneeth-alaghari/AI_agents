"""
Email Housekeeper - Pydantic Schemas
========================================
Request/response schemas for email endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────

class EmailRunRequest(BaseModel):
    """Request body for POST /email/run."""
    auto_mode: bool = Field(
        default=False,
        description="Enable auto-execution for high-confidence decisions",
    )
    max_emails: int = Field(
        default=20, ge=1, le=100,
        description="Maximum number of emails to process",
    )


class FeedbackRequest(BaseModel):
    """Request body for POST /email/feedback."""
    email_record_id: int = Field(..., description="ID of the email record")
    user_action: str = Field(
        ...,
        pattern="^(keep|delete)$",
        description="User's chosen action: 'keep' or 'delete'",
    )


# ── Response Schemas ─────────────────────────────────────

class EmailRunResponse(BaseModel):
    """Stats returned after processing emails."""
    total_processed: int
    deleted: int
    kept: int
    needs_review: int
    auto_executed: int
    priority_breakdown: dict


class EmailReviewItem(BaseModel):
    """Single email awaiting manual review."""
    id: int
    email_id: str
    subject: Optional[str]
    sender: Optional[str]
    snippet: Optional[str]
    priority: int
    suggested_action: str
    final_score: float
    processed_at: Optional[datetime]


class EmailStatsResponse(BaseModel):
    """24-hour processing statistics."""
    total_processed_24h: int
    deleted_count: int
    kept_count: int
    needs_review_count: int
    auto_executed_count: int
    priority_breakdown: dict
    avg_confidence: float


class FeedbackResponse(BaseModel):
    """Feedback submission result."""
    feedback_id: int
    email_record_id: int
    original_action: str
    user_action: str
    is_override: bool
    message: str
