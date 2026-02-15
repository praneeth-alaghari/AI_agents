"""
Email Housekeeper - Core Service
====================================
Business logic for email processing pipeline.

Pipeline: Fetch → Classify (LLM) → Embed → Reinforce (Memory) → Decide → Store
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.sections.personal_management.email_housekeeper.models import (
    EmailRecord, FeedbackRecord, EmailAction,
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


# ── Mock Email Data (replace with Gmail API later) ───────
MOCK_EMAILS = [
    {
        "email_id": "msg_001",
        "subject": "URGENT: Server Down - Production Alert",
        "sender": "alerts@company.com",
        "snippet": "Production server p-east-1 is not responding. Immediate action required.",
    },
    {
        "email_id": "msg_002",
        "subject": "Weekly Newsletter - Tech Updates",
        "sender": "newsletter@techdigest.com",
        "snippet": "This week in tech: AI breakthroughs, new Python release, and more...",
    },
    {
        "email_id": "msg_003",
        "subject": "Your Amazon Order Has Shipped",
        "sender": "shipping@amazon.com",
        "snippet": "Your order #123-456 has been shipped and will arrive by Thursday.",
    },
    {
        "email_id": "msg_004",
        "subject": "Meeting Tomorrow at 10 AM",
        "sender": "boss@company.com",
        "snippet": "Hi, let's discuss the Q2 roadmap tomorrow at 10 AM in Conference Room B.",
    },
    {
        "email_id": "msg_005",
        "subject": "You've Won a Free iPhone!!!",
        "sender": "promo@spam-deals.xyz",
        "snippet": "Congratulations! Click here to claim your free iPhone 15 Pro Max!!!",
    },
    {
        "email_id": "msg_006",
        "subject": "Invoice #INV-2024-0892",
        "sender": "billing@saasprovider.com",
        "snippet": "Your monthly invoice for $49.99 is ready. Payment due by Feb 28.",
    },
    {
        "email_id": "msg_007",
        "subject": "GitHub: Pull Request Review Requested",
        "sender": "notifications@github.com",
        "snippet": "JaneDoe requested your review on PR #342: Fix authentication middleware.",
    },
    {
        "email_id": "msg_008",
        "subject": "Lunch plans?",
        "sender": "friend@gmail.com",
        "snippet": "Hey! Are you free for lunch today? There's a new place downtown.",
    },
    {
        "email_id": "msg_009",
        "subject": "Password Reset Request",
        "sender": "security@bank.com",
        "snippet": "We received a request to reset your password. If this wasn't you, contact us.",
    },
    {
        "email_id": "msg_010",
        "subject": "50% OFF Everything - Limited Time!",
        "sender": "deals@randomstore.com",
        "snippet": "Massive clearance sale! Everything must go. Use code SAVE50 at checkout.",
    },
]


class EmailHousekeeperService:
    """Core service orchestrating the email processing pipeline."""

    def __init__(
        self,
        classifier: EmailClassifier,
        reinforcement: ReinforcementService,
        vector_service: EmailVectorService,
    ):
        self.classifier = classifier
        self.reinforcement = reinforcement
        self.vector_service = vector_service

    # ── POST /email/run ──────────────────────────────────

    async def process_emails(
        self,
        user_id: int,
        db: AsyncSession,
        auto_mode: bool = False,
        max_emails: int = 20,
    ) -> Dict[str, Any]:
        """Process a batch of emails through the AI classification pipeline."""
        
        
        # Check for User's Gmail Key
        from app.models.api_keys import UserAPIKey
        from app.sections.personal_management.email_housekeeper.gmail_client import GmailClient
        from app.core.config import get_settings
        
        settings = get_settings()
        
        result = await db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.service_name == "gmail"
            )
        )
        api_key_record = result.scalar_one_or_none()
        
        emails = []
        token_to_use = None
        
        # Priority 1: User-specific key from DB
        if api_key_record:
            token_to_use = api_key_record.api_key
        # Priority 2: Server-wide default key (fallback)
        elif settings.DEFAULT_GMAIL_TOKEN:
            token_to_use = settings.DEFAULT_GMAIL_TOKEN
            
        if token_to_use:
            try:
                client = GmailClient(token_to_use)
                emails = client.fetch_emails(max_results=max_emails)
            except Exception as e:
                print(f"Gmail fetch failed: {e}")
                emails = []
                # Fallback disabled to ensure only real data is shown
                # if not emails:
                #     emails = MOCK_EMAILS[:max_emails]
        else:
             # Fallback disabled
             # emails = MOCK_EMAILS[:max_emails]
             emails = []

        # Fetch existing email_ids for today to prevent duplicates
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        existing_q = await db.execute(
            select(EmailRecord.email_id).where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= cutoff_time
            )
        )
        existing_ids = set(existing_q.scalars().all())

        stats = {
            "total_processed": 0,
            "deleted": 0,
            "kept": 0,
            "needs_review": 0,
            "auto_executed": 0,
            "priority_breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }

        for email_data in emails:
            if email_data["email_id"] in existing_ids:
                continue

            try:
                result = await self._process_single_email(
                    user_id=user_id,
                    db=db,
                    email_data=email_data,
                    auto_mode=auto_mode,
                )

                stats["total_processed"] += 1
                stats["priority_breakdown"][result["priority"]] += 1

                if result["action"] == EmailAction.DELETE.value:
                    stats["deleted"] += 1
                elif result["action"] == EmailAction.KEEP.value:
                    stats["kept"] += 1
                else:
                    stats["needs_review"] += 1

                if result.get("auto_executed"):
                    stats["auto_executed"] += 1

            except Exception:
                continue  # Log error but don't stop the batch

        return stats

    async def _process_single_email(
        self,
        user_id: int,
        db: AsyncSession,
        email_data: Dict[str, Any],
        auto_mode: bool,
    ) -> Dict[str, Any]:
        """
        Pipeline for a single email:
        1. Classify with LLM
        2. Generate embedding
        3. Enhance with reinforcement memory
        4. Determine final action
        5. Store record in DB
        6. Store in vector memory
        """

        email_text = (
            f"{email_data['subject']} {email_data['sender']} {email_data['snippet']}"
        )

        # Step 1: LLM classification
        llm_result = await self.classifier.classify(
            subject=email_data["subject"],
            sender=email_data["sender"],
            snippet=email_data["snippet"],
        )

        # Step 2: Generate embedding
        embedding = await self.vector_service.generate_embedding(email_text)

        # Step 3: Reinforce with memory
        enhanced = await self.reinforcement.enhance_decision(
            user_id=user_id,
            email_text=email_text,
            llm_result=llm_result,
            embedding=embedding,
        )

        # Step 4: Final action decision
        action = enhanced["action"]
        auto_executed = False

        if auto_mode and enhanced["auto_execute"]:
            auto_executed = True
        elif not auto_mode:
            if enhanced["final_score"] < 0.85:
                action = EmailAction.REVIEW.value

        # Step 5: Persist to database
        record = EmailRecord(
            user_id=user_id,
            email_id=email_data["email_id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            snippet=email_data["snippet"],
            priority=enhanced["priority"],
            action=action,
            llm_confidence=enhanced["llm_confidence"],
            vector_similarity=enhanced["vector_similarity"],
            rule_weight=enhanced["rule_weight"],
            final_score=enhanced["final_score"],
            auto_executed=auto_executed,
        )
        db.add(record)
        await db.flush()

        # Step 6: Store in vector memory - DISABLED per user request
        # We only store in vector memory when user checks "Wrong Category" (Feedback Loop)
        # await self.vector_service.store_memory(
        #     user_id=user_id,
        #     text=email_text,
        #     embedding=embedding,
        #     action=action,
        #     priority=enhanced["priority"],
        # )

        return {
            "id": record.id,
            "action": action,
            "priority": enhanced["priority"],
            "final_score": enhanced["final_score"],
            "auto_executed": auto_executed,
        }

    # ── GET /email/stats ─────────────────────────────────

    async def get_stats(
        self, user_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        """Get email processing stats for the last 24 hours."""

        since = datetime.now(timezone.utc) - timedelta(hours=24)

        # Total processed
        total_q = await db.execute(
            select(func.count(EmailRecord.id)).where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= since,
            )
        )
        total = total_q.scalar() or 0

        # Action breakdown
        action_q = await db.execute(
            select(EmailRecord.action, func.count(EmailRecord.id))
            .where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= since,
            )
            .group_by(EmailRecord.action)
        )
        action_counts = {row[0]: row[1] for row in action_q.all()}

        # Priority breakdown
        priority_q = await db.execute(
            select(EmailRecord.priority, func.count(EmailRecord.id))
            .where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= since,
            )
            .group_by(EmailRecord.priority)
        )
        priority_counts = {str(row[0]): row[1] for row in priority_q.all()}

        # Auto-executed count
        auto_q = await db.execute(
            select(func.count(EmailRecord.id)).where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= since,
                EmailRecord.auto_executed == True,
            )
        )
        auto_count = auto_q.scalar() or 0

        # Average confidence
        avg_q = await db.execute(
            select(func.avg(EmailRecord.final_score)).where(
                EmailRecord.user_id == user_id,
                EmailRecord.processed_at >= since,
            )
        )
        avg_confidence = round(float(avg_q.scalar() or 0), 3)

        return {
            "total_processed_24h": total,
            "deleted_count": action_counts.get("delete", 0),
            "kept_count": action_counts.get("keep", 0),
            "needs_review_count": action_counts.get("needs_review", 0),
            "auto_executed_count": auto_count,
            "priority_breakdown": priority_counts,
            "avg_confidence": avg_confidence,
        }

    # ── GET /email/review ────────────────────────────────

    async def get_review_emails(
        self, user_id: int, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get emails marked for manual review (low-confidence) from the last 24 hours."""
        
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        result = await db.execute(
            select(EmailRecord)
            .where(
                EmailRecord.user_id == user_id,
                EmailRecord.action == EmailAction.REVIEW.value,
                EmailRecord.processed_at >= since,
            )
            .order_by(EmailRecord.processed_at.desc())
            .limit(50)
        )
        records = result.scalars().all()

        return [
            {
                "id": r.id,
                "email_id": r.email_id,
                "subject": r.subject,
                "sender": r.sender,
                "snippet": r.snippet,
                "priority": r.priority,
                "suggested_action": r.action,
                "final_score": r.final_score,
                "processed_at": (
                    r.processed_at.isoformat() if r.processed_at else None
                ),
            }
            for r in records
        ]

    # ── POST /email/feedback ─────────────────────────────

    async def submit_feedback(
        self,
        user_id: int,
        db: AsyncSession,
        email_record_id: int,
        user_action: str,
    ) -> Dict[str, Any]:
        """
        Process user feedback and store in reinforcement memory.
        This is how the system learns without retraining.
        """

        # Get the email record (user-scoped)
        result = await db.execute(
            select(EmailRecord).where(
                EmailRecord.id == email_record_id,
                EmailRecord.user_id == user_id,
            )
        )
        email_record = result.scalar_one_or_none()

        if not email_record:
            raise ValueError(
                "Email record not found or does not belong to this user"
            )

        is_override = email_record.action != user_action

        failure_message = None

        # If action is DELETE, move to Trash in Gmail
        if user_action == EmailAction.DELETE.value:
            try:
                from app.models.api_keys import UserAPIKey
                from app.sections.personal_management.email_housekeeper.gmail_client import GmailClient
                from app.core.config import get_settings
                
                settings = get_settings()
                key_q = await db.execute(
                    select(UserAPIKey.api_key).where(
                        UserAPIKey.user_id == user_id, 
                        UserAPIKey.service_name == 'gmail'
                    )
                )
                user_token = key_q.scalar_one_or_none()
                token = user_token or settings.DEFAULT_GMAIL_TOKEN
                
                if token:
                    client = GmailClient(token)
                    success = client.trash_email(email_record.email_id)
                    if success:
                        print(f"Successfully trashed email {email_record.email_id} in Gmail")
                    else:
                        failure_message = "Gmail API returned False"
            except Exception as e:
                print(f"Failed to execute Gmail deletion logic: {e}")
                failure_message = str(e)

        # Store feedback record
        feedback = FeedbackRecord(
            user_id=user_id,
            email_record_id=email_record_id,
            original_action=email_record.action,
            user_action=user_action,
            is_override=is_override,
        )
        db.add(feedback)

        # Update the email record's action
        email_record.action = user_action

        # Store correction in vector memory for future learning
        try:
            email_text = (
                f"{email_record.subject} {email_record.sender} {email_record.snippet}"
            )
            embedding = await self.vector_service.generate_embedding(email_text)

            await self.reinforcement.store_feedback_memory(
                user_id=user_id,
                email_text=email_text,
                embedding=embedding,
                user_action=user_action,
                priority=email_record.priority,
            )
        except Exception as e:
            print(f"Warning: Failed to learn from feedback (Vector/Embedding service offline?): {e}")

        await db.flush()

        return {
            "feedback_id": feedback.id,
            "email_record_id": email_record_id,
            "original_action": feedback.original_action,
            "user_action": user_action,
            "is_override": is_override,
            "message": "Feedback recorded." if not failure_message else f"Feedback saved, but Gmail deletion failed: {failure_message}",
        }
