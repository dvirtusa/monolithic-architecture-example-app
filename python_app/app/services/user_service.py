import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models import UserCreate, UserResponse, UserInDB, UserLogin, Token
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    DatabaseException,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        try:
            now = datetime.now(timezone.utc)
            user_dict = {
                "name": user_data.name,
                "email": user_data.email,
                "hashed_password": get_password_hash(user_data.password),
                "created_at": now,
                "updated_at": now,
            }

            result = await self.collection.insert_one(user_dict)
            
            created_user = await self.collection.find_one({"_id": result.inserted_id})
            if created_user is None:
                raise DatabaseException("user creation", "Failed to retrieve created user")

            return UserResponse(
                _id=str(created_user["_id"]),
                name=created_user["name"],
                email=created_user["email"],
                created_at=created_user["created_at"],
            )
        except DuplicateKeyError:
            logger.warning(f"Attempted to create duplicate user with email: {user_data.email}")
            raise UserAlreadyExistsException(user_data.email)
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise DatabaseException("user creation", str(e))

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        user = await self.get_user_by_email(login_data.email)
        if user is None:
            logger.warning(f"Login attempt for non-existent user: {login_data.email}")
            raise InvalidCredentialsException()

        if not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {login_data.email}")
            raise InvalidCredentialsException()

        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User logged in successfully: {login_data.email}")
        return Token(access_token=access_token)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        try:
            user = await self.collection.find_one({"email": email})
            if user is None:
                return None
            return UserInDB(
                _id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                hashed_password=user["hashed_password"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            )
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            raise DatabaseException("user lookup", str(e))

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        try:
            if not ObjectId.is_valid(user_id):
                return None
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user is None:
                return None
            return UserInDB(
                _id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                hashed_password=user["hashed_password"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            )
        except Exception as e:
            logger.error(f"Error fetching user by id: {e}")
            raise DatabaseException("user lookup", str(e))

    async def get_user_response_by_email(self, email: str) -> UserResponse:
        user = await self.get_user_by_email(email)
        if user is None:
            raise UserNotFoundException(email)
        return UserResponse(
            _id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
