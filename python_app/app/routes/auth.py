import logging
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.services import UserService
from app.utils.security import get_current_user_required
from app.utils.exceptions import (
    AppException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    return UserService(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User successfully registered"},
        409: {"description": "User with this email already exists"},
        422: {"description": "Validation error"},
    },
)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"New user registered: {user.email}")
        return user
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AppException as e:
        logger.error(f"Error during registration: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service),
) -> Token:
    try:
        token = await user_service.authenticate_user(login_data)
        return token
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AppException as e:
        logger.error(f"Error during login: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user_required),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = await user_service.get_user_response_by_email(current_user.email)
        return user
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
