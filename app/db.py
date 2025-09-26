from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    await db.schedules.create_index("status")
    await db.schedules.create_index("run_at")
    return db

async def get_db():
    if db is None:
        await init_db()
    return db