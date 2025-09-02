from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.npc_repo import NPCRepository, NpcReplicaRepository
from app.schemas.npc import NPCCreate, NpcReplicaCreate, DialogueRequest
from app.core.redis import redis
from typing import List, Optional, Dict, Any
import json

class NPCService:
    def __init__(self, session: AsyncSession):
        self.npc_repo = NPCRepository(session)
        self.replica_repo = NpcReplicaRepository(session)

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

    async def process_dialogue(self, dialogue_request: DialogueRequest) -> dict:
        """Handle NPC dialogue"""
        npc = await self.get_npc(dialogue_request.npc_id)
        if not npc:
            raise ValueError("NPC not found")
        
        # Save player's message
        player_replica = NpcReplicaCreate(
            npc_id=dialogue_request.npc_id,
            text=dialogue_request.message,
            is_player_message=True,
            session_id=dialogue_request.session_id
        )
        await self.replica_repo.create_replica(player_replica)
        
        # Get NPC memory
        npc_memory = await self.get_npc_memory(dialogue_request.npc_id, dialogue_request.session_id)
        
        # Get dialogue history
        dialogue_history = await self.replica_repo.get_npc_dialogue_history(
            dialogue_request.npc_id, 
            dialogue_request.session_id
        )
        
        # Generate NPC response (placeholder: should be integrated with AI)
        npc_response = await self._generate_npc_response(
            npc, 
            dialogue_request.message, 
            npc_memory, 
            dialogue_history
        )
        
        # Save NPC response
        npc_replica = NpcReplicaCreate(
            npc_id=dialogue_request.npc_id,
            text=npc_response,
            is_player_message=False,
            session_id=dialogue_request.session_id
        )
        await self.replica_repo.create_replica(npc_replica)
        
        # Update NPC memory
        memory_entry = {
            "player_message": dialogue_request.message,
            "npc_response": npc_response,
            "timestamp": str(dialogue_request.npc_id)  # Should be a real timestamp in production
        }
        await self.save_npc_memory(dialogue_request.npc_id, memory_entry, dialogue_request.session_id)
        
        return {
            "npc_response": npc_response,
            "npc_info": npc,
            "memory_updated": True
        }

    async def _generate_npc_response(self, npc: dict, player_message: str, memory: List[dict], history: List[dict]) -> str:
        """Generate NPC response based on character type and context"""
        # Very simplified version. Should be integrated with an LLM in real project.
        
        character_responses = {
            "worker": {
                "greeting": "Hey... I'm tired after my shift. What do you want?",
                "problems": "I work for peanuts, the boss treats me badly. Living in a dorm with ten people.",
                "default": "I don’t know... maybe you’re right. But what can I do?"
            },
            "entrepreneur": {
                "greeting": "Welcome! I'm always open to new business opportunities.",
                "problems": "Bureaucracy is killing us! Taxes are rising, no support at all. Corruption everywhere.",
                "default": "Interesting idea... But I need to think about risks and profit."
            },
            "activist": {
                "greeting": "Hi! Do you also care about our city's environment?",
                "problems": "Air is toxic, rivers are polluted! Authorities don’t do anything!",
                "default": "We must act! Protests, rallies – that’s the only way to change things!"
            },
            "pensioner": {
                "greeting": "Hello, young one. How are you?",
                "problems": "The pension is too small, medicines are expensive. Doctors don’t treat, they harm.",
                "default": "In my time things were different... But maybe you’re right about the future."
            },
            "official": {
                "greeting": "Welcome. How can I help?",
                "problems": "It’s hard to balance everyone’s interests. Every decision upsets someone.",
                "default": "This requires careful consideration. We must take everything into account."
            }
        }
        
        # Simple response selection logic
        message_lower = player_message.lower()
        
        if any(word in message_lower for word in ["hi", "hello", "welcome"]):
            return character_responses[npc["character_type"]]["greeting"]
        elif any(word in message_lower for word in ["problem", "what happened", "how are you"]):
            return character_responses[npc["character_type"]]["problems"]
        else:
            return character_responses[npc["character_type"]]["default"]

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
