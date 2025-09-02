from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    progress = Column(Text, default="{}")

    user = relationship("User", back_populates="sessions")
