"""
myAgentAI - API Keys Router
===============================
Manage per-user API keys for external services.

Rules:
  - OpenAI: Falls back to system default if not provided.
  - Gmail:  MUST be user-provided (no system default).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.models.user import User
from app.models.api_keys import UserAPIKey
from app.schemas.user import APIKeyCreate, APIKeyResponse
from app.utils.constants import SUPPORTED_SERVICES


router = APIRouter(prefix="/api-keys", tags=["API Key Management"])


@router.post("/")
async def store_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Store or update an API key for a service."""

    if key_data.service_name not in SUPPORTED_SERVICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                message=f"Unsupported service. Choose from: {SUPPORTED_SERVICES}"
            ),
        )

    # Check if key already exists
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.service_name == key_data.service_name,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.encrypted_key = key_data.api_key  # TODO: encrypt in production
        message = f"{key_data.service_name} API key updated successfully"
    else:
        new_key = UserAPIKey(
            user_id=current_user.id,
            service_name=key_data.service_name,
            encrypted_key=key_data.api_key,  # TODO: encrypt in production
        )
        db.add(new_key)
        message = f"{key_data.service_name} API key stored successfully"

    await db.flush()
    return success_response(message=message)


@router.get("/")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all stored API keys for the current user (keys are masked)."""

    result = await db.execute(
        select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    )
    keys = result.scalars().all()

    key_list = [
        {
            "id": k.id,
            "service_name": k.service_name,
            "is_set": True,
            "created_at": k.created_at.isoformat() if k.created_at else None,
        }
        for k in keys
    ]

    return success_response(
        message=f"Found {len(key_list)} API key(s)",
        data=key_list,
    )


@router.delete("/{service_name}")
async def delete_api_key(
    service_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an API key for a specific service."""

    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.service_name == service_name,
        )
    )
    key = result.scalar_one_or_none()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message=f"No {service_name} key found"),
        )

    await db.delete(key)
    return success_response(message=f"{service_name} API key deleted successfully")
