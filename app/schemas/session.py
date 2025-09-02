from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class GameSessionBase(BaseModel):
    progress: Dict[str, Any] = {}

class GameSessionCreate(GameSessionBase):
    user_id: int

class GameSession(GameSessionBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GameSessionUpdate(BaseModel):
    progress: Optional[Dict[str, Any]] = None
