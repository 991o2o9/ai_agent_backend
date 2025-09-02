from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.session_repo import SessionRepository
from app.schemas.session import GameSessionCreate, GameSessionUpdate
from typing import List, Optional, Dict, Any

class SessionService:
    def __init__(self, session: AsyncSession):
        self.session_repo = SessionRepository(session)

    async def create_session(self, user_id: int, initial_progress: Dict[str, Any] = None) -> dict:
        if initial_progress is None:
            initial_progress = {
                "current_location": {"x": 0, "y": 0},
                "visited_npcs": [],
                "completed_dialogues": {},
                "game_state": "started"
            }
        
        session_data = GameSessionCreate(
            user_id=user_id,
            progress=initial_progress
        )
        
        game_session = await self.session_repo.create_session(session_data)
        return game_session

    async def get_session(self, session_id: int) -> Optional[dict]:
        return await self.session_repo.get_session_by_id(session_id)

    async def get_user_sessions(self, user_id: int) -> List[dict]:
        return await self.session_repo.get_user_sessions(user_id)

    async def update_session_progress(self, session_id: int, progress_updates: Dict[str, Any]) -> Optional[dict]:
        # Получаем текущую сессию
        current_session = await self.session_repo.get_session_by_id(session_id)
        if not current_session:
            return None
        
        # Обновляем прогресс
        updated_progress = current_session.progress.copy()
        updated_progress.update(progress_updates)
        
        session_data = GameSessionUpdate(progress=updated_progress)
        return await self.session_repo.update_session(session_id, session_data)

    async def add_visited_npc(self, session_id: int, npc_id: int) -> bool:
        current_session = await self.session_repo.get_session_by_id(session_id)
        if not current_session:
            return False
        
        visited_npcs = current_session.progress.get("visited_npcs", [])
        if npc_id not in visited_npcs:
            visited_npcs.append(npc_id)
            
        progress_updates = {"visited_npcs": visited_npcs}
        result = await self.update_session_progress(session_id, progress_updates)
        return result is not None

    async def mark_dialogue_completed(self, session_id: int, npc_id: int, dialogue_id: str) -> bool:
        current_session = await self.session_repo.get_session_by_id(session_id)
        if not current_session:
            return False
        
        completed_dialogues = current_session.progress.get("completed_dialogues", {})
        if str(npc_id) not in completed_dialogues:
            completed_dialogues[str(npc_id)] = []
        
        if dialogue_id not in completed_dialogues[str(npc_id)]:
            completed_dialogues[str(npc_id)].append(dialogue_id)
            
        progress_updates = {"completed_dialogues": completed_dialogues}
        result = await self.update_session_progress(session_id, progress_updates)
        return result is not None

    async def delete_session(self, session_id: int) -> bool:
        return await self.session_repo.delete_session(session_id)
