from app.db.base import Base
from app.db.session import engine

# Import all models to ensure they are registered with Base metadata
from app.models.user import User
from app.models.api_keys import UserAPIKey
from app.sections.personal_management.email_housekeeper.models import EmailRecord, FeedbackRecord

async def init_models():
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional: reset
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Tables Created Successfully")
