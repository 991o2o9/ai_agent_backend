from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.session import GameSession
from app.schemas.session import GameSessionCreate, GameSessionUpdate
from typing import Optional, List

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session_data: GameSessionCreate) -> GameSession:
        game_session = GameSession(
            user_id=session_data.user_id,
            progress=session_data.progress
        )
        self.session.add(game_session)
        await self.session.commit()
        await self.session.refresh(game_session)
        return game_session

    async def get_session_by_id(self, session_id: int) -> Optional[GameSession]:
        result = await self.session.execute(
            select(GameSession).options(selectinload(GameSession.user))
            .where(GameSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: int) -> List[GameSession]:
        result = await self.session.execute(
            select(GameSession).where(GameSession.user_id == user_id)
        )
        return result.scalars().all()

    async def update_session(self, session_id: int, session_data: GameSessionUpdate) -> Optional[GameSession]:
        result = await self.session.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        game_session = result.scalar_one_or_none()
        
        if game_session:
            if session_data.progress is not None:
                game_session.progress = session_data.progress
            await self.session.commit()
            await self.session.refresh(game_session)
        
        return game_session

    async def delete_session(self, session_id: int) -> bool:
        result = await self.session.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        game_session = result.scalar_one_or_none()
        
        if game_session:
            await self.session.delete(game_session)
            await self.session.commit()
            return True
        return False
