from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.npc_repo import NPCRepository, NpcReplicaRepository
from app.schemas.npc import NPCCreate, NpcReplicaCreate, DialogueRequest
from app.core.redis import redis
from app.services.ai_service import AIService
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

class NPCService:
    def __init__(self, session: AsyncSession):
        self.npc_repo = NPCRepository(session)
        self.replica_repo = NpcReplicaRepository(session)
        self.ai_service = AIService()

    async def create_npc(self, npc_data: NPCCreate) -> dict:
        return await self.npc_repo.create_npc(npc_data)

    async def get_npc(self, npc_id: int) -> Optional[dict]:
        return await self.npc_repo.get_npc_by_id(npc_id)

    async def get_npc_by_name(self, name: str) -> Optional[dict]:
        return await self.npc_repo.get_npc_by_name(name)

    async def get_all_npcs(self) -> List[dict]:
        return await self.npc_repo.get_all_npcs()

    async def get_npcs_by_type(self, character_type: str) -> List[dict]:
        return await self.npc_repo.get_npcs_by_type(character_type)

    async def get_npc_memory(self, npc_id: int, session_id: Optional[int] = None) -> List[dict]:
        """Get NPC memory from Redis"""
        memory_key = f"npc_memory:{npc_id}"
        if session_id:
            memory_key += f":session:{session_id}"
        
        memory_data = await redis.get(memory_key)
        if memory_data:
            return json.loads(memory_data)
        return []

    async def save_npc_memory(self, npc_id: int, memory_entry: dict, session_id: Optional[int] = None):
        """Save NPC memory into Redis"""
        memory_key = f"npc_memory:{npc_id}"
        if session_id:
            memory_key += f":session:{session_id}"
        
        current_memory = await self.get_npc_memory(npc_id, session_id)
        current_memory.append(memory_entry)
        
        # Keep only the last 20 messages in memory
        if len(current_memory) > 20:
            current_memory = current_memory[-20:]
        
        await redis.set(memory_key, json.dumps(current_memory), ex=3600)  # TTL 1 hour

    async def process_dialogue(self, dialogue_request: DialogueRequest, user_id: int = None) -> dict:
        """Handle NPC dialogue with AI integration"""
        npc = await self.get_npc(dialogue_request.npc_id)
        if not npc:
            raise ValueError("NPC not found")
        
        # Check rate limits if user_id is provided
        if user_id and not await self.ai_service.rate_limit_check(user_id):
            raise ValueError("Rate limit exceeded. Please wait before sending another message.")
        
        # Save player's message
        player_replica = NpcReplicaCreate(
            npc_id=dialogue_request.npc_id,
            text=dialogue_request.message,
            is_player_message=True,
            session_id=dialogue_request.session_id
        )
        await self.replica_repo.create_replica(player_replica)
        
        # Update short-term memory
        session_key = str(dialogue_request.session_id) if dialogue_request.session_id else "global"
        await self.ai_service.update_short_term_memory(
            session_key, 
            dialogue_request.npc_id, 
            dialogue_request.message, 
            True
        )
        
        # Get short-term memory for context
        short_memory = await self.ai_service.get_short_term_memory(
            session_key, 
            dialogue_request.npc_id
        )
        
        # Get long-term memory (dialogue history)
        long_memory = await self.replica_repo.get_npc_dialogue_history(
            dialogue_request.npc_id, 
            dialogue_request.session_id
        )
        
        # Build personality string
        personality = f"{npc.character_type} - {npc.description}"
        if npc.personality_traits:
            personality += f". Traits: {', '.join(npc.personality_traits)}"
        if npc.problems:
            personality += f". Problems: {', '.join(npc.problems)}"
        
        try:
            # Generate AI response
            npc_response = await self.ai_service.generate_response(
                prompt=dialogue_request.message,
                context=short_memory,
                npc_personality=personality
            )
        except Exception as ai_error:
            # If AI fails, we can't continue - this is a hackathon requirement
            raise ValueError(f"AI service unavailable: {str(ai_error)}")
        
        # Save NPC response
        npc_replica = NpcReplicaCreate(
            npc_id=dialogue_request.npc_id,
            text=npc_response,
            is_player_message=False,
            session_id=dialogue_request.session_id
        )
        await self.replica_repo.create_replica(npc_replica)
        
        # Update short-term memory with NPC response
        await self.ai_service.update_short_term_memory(
            session_key, 
            dialogue_request.npc_id, 
            npc_response, 
            False
        )
        
        # Update long-term memory in database
        memory_entry = {
            "player_message": dialogue_request.message,
            "npc_response": npc_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.save_npc_memory(dialogue_request.npc_id, memory_entry, dialogue_request.session_id)
        
        return {
            "npc_response": npc_response,
            "npc_info": npc,
            "memory_updated": True,
            "ai_generated": True
        }

    async def initialize_default_npcs(self):
        """Initialize default NPCs for the game"""
        default_npcs = [
            {
                "name": "Ali",
                "character_type": "worker",
                "description": "Migrant worker, tired and suspicious, but can open up in an honest talk.",
                "personality_traits": ["tired", "suspicious", "honest"],
                "problems": ["low salary", "tough conditions", "discrimination"],
                "location_x": 100,
                "location_y": 200
            },
            {
                "name": "Dana",
                "character_type": "entrepreneur", 
                "description": "Ambitious entrepreneur, frustrated with the system, looking for support.",
                "personality_traits": ["ambitious", "dissatisfied", "seeking support"],
                "problems": ["bureaucracy", "taxes", "corruption"],
                "location_x": 300,
                "location_y": 150
            },
            {
                "name": "Arman",
                "character_type": "activist",
                "description": "Environmental activist, idealistic, emotional, sometimes radical.",
                "personality_traits": ["idealistic", "emotional", "radical"],
                "problems": ["air pollution", "water pollution"],
                "location_x": 200,
                "location_y": 300
            },
            {
                "name": "Bakai",
                "character_type": "pensioner",
                "description": "Wise pensioner, nostalgic about the past but wants a better future.",
                "personality_traits": ["wise", "nostalgic", "optimistic"],
                "problems": ["low pension", "poor healthcare"],
                "location_x": 150,
                "location_y": 100
            },
            {
                "name": "Zarina",
                "character_type": "official",
                "description": "Pragmatic official, cautious, speaks in a formal tone.",
                "personality_traits": ["pragmatic", "cautious", "formal"],
                "problems": ["balancing interests", "elite pressure"],
                "location_x": 400,
                "location_y": 250
            }
        ]
        
        for npc_data in default_npcs:
            existing_npc = await self.get_npc_by_name(npc_data["name"])
            if not existing_npc:
                await self.create_npc(NPCCreate(**npc_data))
