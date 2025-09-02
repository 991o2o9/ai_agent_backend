from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from datetime import datetime
from app.core.db import Base

class NPC(Base):
    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    character_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    personality_traits = Column(JSON, default=list)
    problems = Column(JSON, default=list)
    location_x = Column(Integer, default=0)
    location_y = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NpcReplica(Base):
    __tablename__ = "npc_replicas"

    id = Column(Integer, primary_key=True, index=True)
    npc_id = Column(Integer, nullable=False, index=True)
    text = Column(Text, nullable=False)
    is_player_message = Column(Boolean, default=False)
    session_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
