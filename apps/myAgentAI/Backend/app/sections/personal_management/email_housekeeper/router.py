"""
Email Housekeeper - API Router
=================================
Endpoints:
  POST /email/run      — Process emails through AI pipeline
  GET  /email/stats    — 24h processing statistics
  GET  /email/review   — Low-confidence emails for manual review
  POST /email/feedback — User feedback for reinforcement learning
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.models.user import User

from app.sections.personal_management.email_housekeeper.schemas import (
    EmailRunRequest,
    FeedbackRequest,
)
from app.sections.personal_management.email_housekeeper.service import (
    EmailHousekeeperService,
)
from app.sections.personal_management.email_housekeeper.classifier import (
    EmailClassifier,
)
from app.sections.personal_management.email_housekeeper.reinforcement import (
    ReinforcementService,
)
from app.sections.personal_management.email_housekeeper.vector_service import (
    EmailVectorService,
)
from app.services.openai_service import OpenAIService
from app.core.config import get_settings


router = APIRouter(prefix="/email", tags=["Email Housekeeper"])
settings = get_settings()


def _build_service(user: User) -> EmailHousekeeperService:
    """
    Factory: builds the service with all dependencies wired up.
    Resolves OpenAI key per user (fallback to system default).
    """
    # TODO: look up user's OpenAI key from DB; for now, use system default
    openai_key = settings.OPENAI_API_KEY
    openai_service = OpenAIService(api_key=openai_key)
    vector_service = EmailVectorService(openai_service=openai_service)
    classifier = EmailClassifier(openai_service=openai_service)
    reinforcement = ReinforcementService(vector_service=vector_service)

    return EmailHousekeeperService(
        classifier=classifier,
        reinforcement=reinforcement,
        vector_service=vector_service,
    )


# ── POST /email/run ──────────────────────────────────────

@router.post("/run")
async def run_email_processing(
    request: EmailRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process emails through the AI classification pipeline.

    - Fetches emails (mock for now)
    - Classifies using OpenAI
    - Applies reinforcement memory
    - Returns processing stats
    """
    try:
        service = _build_service(current_user)
        stats = await service.process_emails(
            user_id=current_user.id,
            db=db,
            auto_mode=request.auto_mode,
            max_emails=request.max_emails,
        )
        return success_response(
            message="Email processing completed successfully",
            data=stats,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message=f"Failed to process emails: {str(e)}"
            ),
        )


# ── GET /email/stats ─────────────────────────────────────

@router.get("/stats")
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get email processing statistics for the last 24 hours."""
    try:
        service = _build_service(current_user)
        stats = await service.get_stats(user_id=current_user.id, db=db)
        return success_response(
            message="Email stats retrieved successfully",
            data=stats,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message=f"Failed to retrieve stats: {str(e)}"
            ),
        )


# ── GET /email/review ────────────────────────────────────

@router.get("/review")
async def get_review_emails(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get emails marked for manual review (low-confidence decisions)."""
    try:
        service = _build_service(current_user)
        emails = await service.get_review_emails(
            user_id=current_user.id, db=db
        )
        return success_response(
            message=f"Found {len(emails)} emails for review",
            data=emails,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message=f"Failed to retrieve review emails: {str(e)}"
            ),
        )


# ── POST /email/feedback ─────────────────────────────────

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit user feedback on an email decision.

    Feeds into reinforcement memory:
    - Stores structured feedback in PostgreSQL
    - Updates vector embeddings in Qdrant
    - Adjusts future decision confidence
    """
    try:
        service = _build_service(current_user)
        result = await service.submit_feedback(
            user_id=current_user.id,
            db=db,
            email_record_id=request.email_record_id,
            user_action=request.user_action,
        )
        return success_response(
            message="Feedback recorded. System will learn from this.",
            data=result,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message=str(e)),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message=f"Failed to submit feedback: {str(e)}"
            ),
        )
