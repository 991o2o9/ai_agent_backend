from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import async_session_maker
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.core.security import verify_token
from typing import Annotated

router = APIRouter()
security = HTTPBearer()

async def get_db():
    async with async_session_maker() as session:
        yield session

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> User:
    # Exception to raise if credentials are invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(credentials.credentials)
    if username is None:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    user_service = UserService(db)
    try:
        result = await user_service.create_user(user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """User login"""
    user_service = UserService(db)
    result = await user_service.authenticate_user(user_data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get info about the currently logged-in user"""
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user info by their ID"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
