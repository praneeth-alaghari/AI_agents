"""
myAgentAI - Scoring Utilities
===============================
Hybrid scoring logic for reinforcement learning decisions.

Formula:
    final_score = (llm_confidence * 0.6)
                + (vector_similarity * 0.3)
                + (rule_weight * 0.1)
"""

from app.core.config import get_settings

settings = get_settings()


def calculate_final_score(
    llm_confidence: float,
    vector_similarity: float,
    rule_weight: float,
) -> float:
    """
    Calculate the hybrid final score from three weighted components.
    Returns a value clamped between 0.0 and 1.0.
    """
    score = (
        (llm_confidence * settings.LLM_CONFIDENCE_WEIGHT)
        + (vector_similarity * settings.VECTOR_SIMILARITY_WEIGHT)
        + (rule_weight * settings.RULE_WEIGHT)
    )
    return round(min(1.0, max(0.0, score)), 4)


def should_auto_execute(final_score: float) -> bool:
    """Determine if an action should be auto-executed based on confidence threshold."""
    return final_score >= settings.AUTO_EXECUTE_THRESHOLD
