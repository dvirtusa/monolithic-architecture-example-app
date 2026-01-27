import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_database() -> None:
    try:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_url}...")
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
        )
        await db.client.admin.command("ping")
        db.db = db.client[settings.database_name]
        
        await create_indexes()
        
        logger.info("Successfully connected to MongoDB")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_database_connection() -> None:
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes() -> None:
    try:
        await db.db.users.create_index("email", unique=True)
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


def get_database() -> AsyncIOMotorDatabase:
    if db.db is None:
        raise RuntimeError("Database not initialized. Call connect_to_database first.")
    return db.db
