from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import Optional

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            password_hash=hashed_password
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).options(selectinload(User.sessions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_with_sessions(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).options(selectinload(User.sessions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
