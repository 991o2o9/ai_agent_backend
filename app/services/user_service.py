from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, hash_password
from app.core.security import create_access_token, create_refresh_token
from typing import Optional
from datetime import timedelta, datetime
from app.core.config import settings

class UserService:
    def __init__(self, session: AsyncSession):
        # Initialize repositories
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)

    async def create_user(self, user_data: UserCreate) -> dict:
        # Check if a user with this username already exists
        existing_user = await self.user_repo.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("A user with this username already exists")
        
        # Create a new user in the database
        user = await self.user_repo.create_user(user_data)
        
        # Generate tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Create refresh token (valid for 7 days)
        refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=timedelta(days=7))
        refresh_expires = datetime.utcnow() + timedelta(days=7)
        await self.refresh_token_repo.create_refresh_token(user.id, refresh_token, refresh_expires)
        
        # Return the tokens along with user info
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            "user": user
        }

    async def authenticate_user(self, user_data: UserLogin) -> Optional[dict]:
        # Try to find the user by username
        user = await self.user_repo.get_user_by_username(user_data.username)
        if not user:
            return None
        
        # Verify the provided password
        if not verify_password(user_data.password, user.password_hash):
            return None
        
        # Revoke all existing refresh tokens for security
        await self.refresh_token_repo.revoke_all_user_tokens(user.id)
        
        # Generate new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Create refresh token (valid for 7 days)
        refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=timedelta(days=7))
        refresh_expires = datetime.utcnow() + timedelta(days=7)
        await self.refresh_token_repo.create_refresh_token(user.id, refresh_token, refresh_expires)
        
        # Return the tokens along with user info
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            "user": user
        }

    async def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """Generate new access token using refresh token"""
        # Verify refresh token JWT
        from app.core.security import verify_refresh_token
        username = verify_refresh_token(refresh_token)
        if not username:
            return None
        
        # Get user
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return None
        
        # Verify that refresh token exists in database and is not revoked
        db_refresh_token = await self.refresh_token_repo.get_refresh_token(refresh_token)
        if not db_refresh_token:
            return None
        
        # Generate new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,  # Return the same refresh token
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            "user": user
        }

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token"""
        return await self.refresh_token_repo.revoke_token(refresh_token)

    async def logout_user(self, user_id: int) -> int:
        """Logout user by revoking all their refresh tokens"""
        return await self.refresh_token_repo.revoke_all_user_tokens(user_id)

    async def get_user_by_id(self, user_id: int):
        # Fetch a user by their ID
        return await self.user_repo.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        # Fetch a user by their username
        return await self.user_repo.get_user_by_username(username)
