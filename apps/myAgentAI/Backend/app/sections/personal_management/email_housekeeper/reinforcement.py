"""
Email Housekeeper - Reinforcement Service
============================================
Memory-augmented decision logic WITHOUT model retraining.

Enhances LLM decisions using vector similarity from past user feedback.
When users override a decision, the correction is stored and influences
future decisions via cosine similarity scoring.
"""

from typing import Dict, Any, List

from app.sections.personal_management.email_housekeeper.vector_service import (
    EmailVectorService,
)
from app.utils.scoring import calculate_final_score, should_auto_execute
from app.core.config import get_settings

settings = get_settings()


class ReinforcementService:
    """Memory-augmented reinforcement layer (no model retraining)."""

    def __init__(self, vector_service: EmailVectorService):
        self.vector_service = vector_service

    async def enhance_decision(
        self,
        user_id: int,
        email_text: str,
        llm_result: Dict[str, Any],
        embedding: List[float],
    ) -> Dict[str, Any]:
        """
        Enhance an LLM classification with vector memory context.

        Steps:
        1. Find similar past decisions from this user's memory
        2. Calculate vector similarity + rule weight
        3. Compute hybrid final_score
        4. Boost confidence if similarity > 0.9
        """

        # Find similar past decisions
        similar_memories = await self.vector_service.find_similar(
            user_id=user_id,
            embedding=embedding,
            top_k=5,
        )

        # Extract best match
        vector_similarity = 0.0
        memory_action = None

        if similar_memories:
            best_match = similar_memories[0]
            vector_similarity = best_match["score"]
            memory_action = best_match["action"]

        # Calculate rule weight from pattern consistency
        rule_weight = self._calculate_rule_weight(similar_memories)

        # Hybrid final score
        llm_confidence = llm_result.get("confidence", 0.5)
        final_score = calculate_final_score(
            llm_confidence=llm_confidence,
            vector_similarity=vector_similarity,
            rule_weight=rule_weight,
        )

        # Determine action
        action = llm_result.get("action", "needs_review")

        # If high similarity with past feedback → trust the memory
        if (
            vector_similarity > settings.SIMILARITY_BOOST_THRESHOLD
            and memory_action
        ):
            action = memory_action
            final_score = min(1.0, final_score + 0.1)  # Confidence boost

        auto_execute = should_auto_execute(final_score)

        return {
            "action": action,
            "priority": llm_result.get("priority", 3),
            "llm_confidence": llm_confidence,
            "vector_similarity": vector_similarity,
            "rule_weight": rule_weight,
            "final_score": final_score,
            "auto_execute": auto_execute,
            "reasoning": llm_result.get("reasoning", ""),
            "memory_influenced": vector_similarity > 0.7,
        }

    def _calculate_rule_weight(
        self, similar_memories: List[Dict[str, Any]]
    ) -> float:
        """
        Determine how consistent past actions were for similar emails.
        High consistency → high rule weight → more confidence.
        """
        if not similar_memories:
            return 0.5  # Neutral when no history

        actions = [m["action"] for m in similar_memories]
        if not actions:
            return 0.5

        most_common = max(set(actions), key=actions.count)
        consistency = actions.count(most_common) / len(actions)
        return consistency

    async def store_feedback_memory(
        self,
        user_id: int,
        email_text: str,
        embedding: List[float],
        user_action: str,
        priority: int,
    ) -> str:
        """Store user feedback as a new memory point for future learning."""
        return await self.vector_service.store_memory(
            user_id=user_id,
            text=email_text,
            embedding=embedding,
            action=user_action,
            priority=priority,
            metadata={"source": "user_feedback"},
        )
