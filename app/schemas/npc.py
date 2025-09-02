from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NPCBase(BaseModel):
    name: str
    character_type: str
    description: str
    personality_traits: List[str] = []
    problems: List[str] = []
    location_x: int = 0
    location_y: int = 0

class NPCCreate(NPCBase):
    pass

class NPC(NPCBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NpcReplicaBase(BaseModel):
    text: str
    is_player_message: bool = False
    session_id: Optional[int] = None

class NpcReplicaCreate(NpcReplicaBase):
    npc_id: int

class NpcReplica(NpcReplicaBase):
    id: int
    npc_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DialogueRequest(BaseModel):
    npc_id: int
    message: str
    session_id: Optional[int] = None

class DialogueRequestAPI(BaseModel):
    message: str
    session_id: Optional[int] = None

class DialogueResponse(BaseModel):
    npc_response: str
    npc_info: dict
    memory_updated: bool
