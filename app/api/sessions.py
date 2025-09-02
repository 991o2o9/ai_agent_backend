from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import async_session_maker
from app.services.session_service import SessionService
from app.schemas.session import GameSession, GameSessionCreate, GameSessionUpdate
from app.api.users import get_current_user
from app.schemas.user import User
from typing import List, Dict, Any

router = APIRouter()

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/", response_model=GameSession)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new game session"""
    session_service = SessionService(db)
    game_session = await session_service.create_session(current_user.id)
    return game_session

@router.get("/", response_model=List[GameSession])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all user sessions"""
    session_service = SessionService(db)
    sessions = await session_service.get_user_sessions(current_user.id)
    return sessions

@router.get("/{session_id}", response_model=GameSession)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session"""
    session_service = SessionService(db)
    game_session = await session_service.get_session(session_id)
    
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check that the session belongs to the current user
    if game_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this session"
        )
    
    return game_session

@router.put("/{session_id}", response_model=GameSession)
async def update_session(
    session_id: int,
    progress_updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update session progress"""
    session_service = SessionService(db)
    
    # Check that the session exists and belongs to the user
    game_session = await session_service.get_session(session_id)
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if game_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this session"
        )
    
    updated_session = await session_service.update_session_progress(session_id, progress_updates)
    return updated_session

@router.post("/{session_id}/visit-npc")
async def visit_npc(
    session_id: int,
    npc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark NPC as visited"""
    session_service = SessionService(db)
    
    # Check access to the session
    game_session = await session_service.get_session(session_id)
    if not game_session or game_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this session"
        )
    
    success = await session_service.add_visited_npc(session_id, npc_id)
    return {"success": success, "message": "NPC marked as visited"}

@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a session"""
    session_service = SessionService(db)
    
    # Check access to the session
    game_session = await session_service.get_session(session_id)
    if not game_session or game_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this session"
        )
    
    success = await session_service.delete_session(session_id)
    return {"success": success, "message": "Session deleted"}
