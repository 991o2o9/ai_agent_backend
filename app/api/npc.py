from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import async_session_maker
from app.services.npc_service import NPCService
from app.schemas.npc import NPC, NPCCreate, NpcReplica, DialogueRequest, DialogueResponse
from app.api.users import get_current_user
from app.schemas.user import User
from typing import List, Optional

router = APIRouter()

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/", response_model=List[NPC])
async def get_all_npcs(
    db: AsyncSession = Depends(get_db)
):
    """Get all NPCs"""
    npc_service = NPCService(db)
    npcs = await npc_service.get_all_npcs()
    return npcs

@router.get("/{npc_id}", response_model=NPC)
async def get_npc(
    npc_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get NPC by ID"""
    npc_service = NPCService(db)
    npc = await npc_service.get_npc(npc_id)
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    return npc

@router.get("/type/{character_type}", response_model=List[NPC])
async def get_npcs_by_type(
    character_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Get NPCs by character type"""
    npc_service = NPCService(db)
    npcs = await npc_service.get_npcs_by_type(character_type)
    return npcs

@router.post("/", response_model=NPC)
async def create_npc(
    npc_data: NPCCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new NPC (admin only)"""
    # In a real project there should be a check for admin rights
    npc_service = NPCService(db)
    npc = await npc_service.create_npc(npc_data)
    return npc

@router.post("/{npc_id}/dialogue")
async def start_dialogue(
    npc_id: int,
    dialogue_request: DialogueRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start dialogue with NPC"""
    npc_service = NPCService(db)
    
    # Set npc_id from URL
    dialogue_request.npc_id = npc_id
    
    try:
        result = await npc_service.process_dialogue(dialogue_request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{npc_id}/memory")
async def get_npc_memory(
    npc_id: int,
    session_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get NPC memory"""
    npc_service = NPCService(db)
    memory = await npc_service.get_npc_memory(npc_id, session_id)
    return {"npc_id": npc_id, "memory": memory}

@router.get("/{npc_id}/dialogue-history")
async def get_dialogue_history(
    npc_id: int,
    session_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get NPC dialogue history"""
    npc_service = NPCService(db)
    history = await npc_service.replica_repo.get_npc_dialogue_history(npc_id, session_id)
    return {"npc_id": npc_id, "history": history}

@router.post("/initialize-default")
async def initialize_default_npcs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initialize default NPCs (admin only)"""
    # In a real project there should be a check for admin rights
    npc_service = NPCService(db)
    await npc_service.initialize_default_npcs()
    return {"message": "Default NPCs initialized"}
