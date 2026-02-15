"""
Email Housekeeper - Vector Service
=====================================
Handles embedding storage and similarity search in Qdrant.
All data is user-scoped — no cross-user memory leakage.
"""

import uuid
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue,
)

from app.services.openai_service import OpenAIService
from app.core.config import get_settings

settings = get_settings()

COLLECTION_NAME = "email_housekeeper_memories"
VECTOR_SIZE = 1536  # text-embedding-3-small output dimension


class EmailVectorService:
    """User-scoped vector memory for email classification decisions."""

    def __init__(self, openai_service: OpenAIService):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.openai_service = openai_service
        self._ensure_collection()

    def _ensure_collection(self):
        """Create the Qdrant collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == COLLECTION_NAME for c in collections):
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception:
            pass  # Qdrant may not be available during startup

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text."""
        return await self.openai_service.create_embedding(text)

    async def store_memory(
        self,
        user_id: int,
        text: str,
        embedding: List[float],
        action: str,
        priority: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store an email decision in vector memory (user-scoped)."""
        point_id = str(uuid.uuid4())
        payload = {
            "user_id": user_id,
            "text": text,
            "action": action,
            "priority": priority,
            **(metadata or {}),
        }

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(id=point_id, vector=embedding, payload=payload)
            ],
        )
        return point_id

    async def find_similar(
        self,
        user_id: int,
        embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find similar past decisions for this user.
        Returns list of matches with score, action, priority.
        """
        try:
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=top_k,
            )

            return [
                {
                    "score": hit.score,
                    "action": hit.payload.get("action", "needs_review"),
                    "priority": hit.payload.get("priority", 3),
                    "text": hit.payload.get("text", ""),
                }
                for hit in results
            ]
        except Exception:
            return []
