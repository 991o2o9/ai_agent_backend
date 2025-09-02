from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.npc import NPC, NpcReplica
from app.schemas.npc import NPCCreate, NpcReplicaCreate
from typing import Optional, List

class NPCRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_npc(self, npc_data: NPCCreate) -> NPC:
        npc = NPC(
            name=npc_data.name,
            character_type=npc_data.character_type,
            description=npc_data.description,
            personality_traits=npc_data.personality_traits,
            problems=npc_data.problems,
            location_x=npc_data.location_x,
            location_y=npc_data.location_y
        )
        self.session.add(npc)
        await self.session.commit()
        await self.session.refresh(npc)
        return npc

    async def get_npc_by_id(self, npc_id: int) -> Optional[NPC]:
        result = await self.session.execute(
            select(NPC).where(NPC.id == npc_id)
        )
        return result.scalar_one_or_none()

    async def get_npc_by_name(self, name: str) -> Optional[NPC]:
        result = await self.session.execute(
            select(NPC).where(NPC.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_npcs(self) -> List[NPC]:
        result = await self.session.execute(
            select(NPC).where(NPC.is_active == True)
        )
        return result.scalars().all()

    async def get_npcs_by_type(self, character_type: str) -> List[NPC]:
        result = await self.session.execute(
            select(NPC).where(
                NPC.character_type == character_type,
                NPC.is_active == True
            )
        )
        return result.scalars().all()

class NpcReplicaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_replica(self, replica_data: NpcReplicaCreate) -> NpcReplica:
        replica = NpcReplica(
            npc_id=replica_data.npc_id,
            text=replica_data.text,
            is_player_message=replica_data.is_player_message,
            session_id=replica_data.session_id
        )
        self.session.add(replica)
        await self.session.commit()
        await self.session.refresh(replica)
        return replica

    async def get_npc_dialogue_history(self, npc_id: int, session_id: Optional[int] = None) -> List[NpcReplica]:
        query = select(NpcReplica).where(NpcReplica.npc_id == npc_id)
        
        if session_id:
            query = query.where(NpcReplica.session_id == session_id)
        
        query = query.order_by(NpcReplica.created_at)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recent_dialogue(self, npc_id: int, limit: int = 10) -> List[NpcReplica]:
        result = await self.session.execute(
            select(NpcReplica)
            .where(NpcReplica.npc_id == npc_id)
            .order_by(NpcReplica.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
