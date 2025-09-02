from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, hash_password
from app.core.security import create_access_token
from typing import Optional
from datetime import timedelta
from app.core.config import settings

class UserService:
    def __init__(self, session: AsyncSession):
        # Initialize user repository
        self.user_repo = UserRepository(session)

    async def create_user(self, user_data: UserCreate) -> dict:
        # Check if a user with this username already exists
        existing_user = await self.user_repo.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("A user with this username already exists")
        
        # Create a new user in the database
        user = await self.user_repo.create_user(user_data)
        
        # Generate an access token for the new user
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Return the token along with user info
        return {
            "access_token": access_token,
            "token_type": "bearer",
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
        
        # Generate an access token for the authenticated user
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Return the token along with user info
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    async def get_user_by_id(self, user_id: int):
        # Fetch a user by their ID
        return await self.user_repo.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        # Fetch a user by their username
        return await self.user_repo.get_user_by_username(username)
