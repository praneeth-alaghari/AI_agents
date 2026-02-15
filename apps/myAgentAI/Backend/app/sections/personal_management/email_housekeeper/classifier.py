"""
Email Housekeeper - Email Classifier
========================================
Uses OpenAI to classify emails by priority and suggest actions.
"""

import json
from typing import Dict, Any

from app.services.openai_service import OpenAIService


CLASSIFICATION_PROMPT = """
You are an email classification assistant. Analyze the following email and provide:

1. priority (1-5): 1=Critical, 2=High, 3=Medium, 4=Low, 5=Spam
2. action: "keep", "delete", or "needs_review"
3. confidence (0.0-1.0): How confident you are in your classification
4. reasoning: Brief explanation

Email:
Subject: {subject}
From: {sender}
Preview: {snippet}

Respond ONLY in valid JSON:
{{"priority": <int>, "action": "<string>", "confidence": <float>, "reasoning": "<string>"}}
"""


class EmailClassifier:
    """Classifies emails using OpenAI LLM."""

    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service

    async def classify(
        self, subject: str, sender: str, snippet: str
    ) -> Dict[str, Any]:
        """
        Classify a single email. Returns dict with:
        priority, action, confidence, reasoning.
        """
        prompt = CLASSIFICATION_PROMPT.format(
            subject=subject or "No Subject",
            sender=sender or "Unknown",
            snippet=snippet or "No preview available",
        )

        try:
            response = await self.openai_service.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise email classifier. Always respond in valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            result = json.loads(response)

            # Validate and sanitize
            result["priority"] = max(1, min(5, int(result.get("priority", 3))))
            result["confidence"] = max(
                0.0, min(1.0, float(result.get("confidence", 0.5)))
            )
            if result.get("action") not in ("keep", "delete", "needs_review"):
                result["action"] = "needs_review"
            result["reasoning"] = result.get("reasoning", "No reasoning provided")

            return result

        except (json.JSONDecodeError, Exception) as e:
            # Graceful fallback — never crash the pipeline
            return {
                "priority": 3,
                "action": "needs_review",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
            }
