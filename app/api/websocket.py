from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.security import verify_token
from app.services.npc_service import NPCService
from app.services.ai_service import AIService
from app.core.db import async_session_maker
from app.core.redis import redis
from typing import Dict, List
import json
import asyncio

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.npc_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, npc_id: int = None):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        if npc_id:
            if npc_id not in self.npc_connections:
                self.npc_connections[npc_id] = []
            self.npc_connections[npc_id].append(websocket)
        
        print(f"User {user_id} connected to WebSocket")

    def disconnect(self, user_id: str, npc_id: int = None):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if npc_id and npc_id in self.npc_connections:
            self.npc_connections[npc_id] = [
                conn for conn in self.npc_connections[npc_id] 
                if conn != self.active_connections.get(user_id)
            ]
        
        print(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast_to_npc(self, message: str, npc_id: int):
        if npc_id in self.npc_connections:
            for connection in self.npc_connections[npc_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove broken connections
                    self.npc_connections[npc_id].remove(connection)

manager = ConnectionManager()

async def get_user_from_token(token: str):
    """Extract user info from JWT token"""
    try:
        username = verify_token(token)
        if not username:
            return None
        
        # Get user from database
        async with async_session_maker() as session:
            from app.repositories.user_repo import UserRepository
            user_repo = UserRepository(session)
            user = await user_repo.get_user_by_username(username)
            return user
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

@router.websocket("/ws/chat/{npc_id}")
async def websocket_endpoint(websocket: WebSocket, npc_id: int):
    """WebSocket endpoint for real-time chat with NPC"""
    user = None
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify token and get user
        user = await get_user_from_token(token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect to WebSocket
        await manager.connect(websocket, str(user.id), npc_id)
        
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": f"Connected to NPC chat. User: {user.username}"
            }),
            str(user.id)
        )
        
        # Handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "message":
                    player_message = message_data.get("message", "")
                    
                    if not player_message.strip():
                        continue
                    
                    # Process message with NPC service
                    async with async_session_maker() as session:
                        npc_service = NPCService(session)
                        
                        # Create dialogue request
                        from app.schemas.npc import DialogueRequest
                        dialogue_request = DialogueRequest(
                            npc_id=npc_id,
                            message=player_message,
                            session_id=message_data.get("session_id")
                        )
                        
                        # Process dialogue
                        try:
                            result = await npc_service.process_dialogue(dialogue_request, user.id)
                            
                            # Send response back to client
                            response_data = {
                                "type": "npc_response",
                                "message": result["npc_response"],
                                "npc_info": result["npc_info"],
                                "timestamp": asyncio.get_event_loop().time()
                            }
                            
                            await manager.send_personal_message(
                                json.dumps(response_data),
                                str(user.id)
                            )
                            
                            # Broadcast to other users chatting with same NPC
                            broadcast_data = {
                                "type": "other_user_message",
                                "user": user.username,
                                "message": player_message,
                                "timestamp": asyncio.get_event_loop().time()
                            }
                            
                            await manager.broadcast_to_npc(
                                json.dumps(broadcast_data),
                                npc_id
                            )
                            
                        except ValueError as ai_error:
                            # Handle AI service errors
                            error_message = str(ai_error)
                            if "AI service unavailable" in error_message:
                                await manager.send_personal_message(
                                    json.dumps({
                                        "type": "error",
                                        "message": "AI service is currently unavailable. Please try again later.",
                                        "details": error_message
                                    }),
                                    str(user.id)
                                )
                            else:
                                await manager.send_personal_message(
                                    json.dumps({
                                        "type": "error",
                                        "message": "Error processing dialogue",
                                        "details": error_message
                                    }),
                                    str(user.id)
                                )
                
                elif message_data.get("type") == "ping":
                    # Handle ping for connection health
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        str(user.id)
                    )
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }),
                    str(user.id)
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Error processing message"
                    }),
                    str(user.id)
                )
                
    except WebSocketDisconnect:
        if user:
            manager.disconnect(str(user.id), npc_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user:
            manager.disconnect(str(user.id), npc_id)
        await websocket.close()

@router.websocket("/ws/status")
async def status_websocket(websocket: WebSocket):
    """WebSocket endpoint for connection status"""
    try:
        await websocket.accept()
        
        # Send current status
        await websocket.send_text(json.dumps({
            "type": "status",
            "active_connections": len(manager.active_connections),
            "npc_connections": {str(k): len(v) for k, v in manager.npc_connections.items()}
        }))
        
        # Keep connection alive for status updates
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            await websocket.send_text(json.dumps({
                "type": "status_update",
                "active_connections": len(manager.active_connections),
                "npc_connections": {str(k): len(v) for k, v in manager.npc_connections.items()}
            }))
            
    except WebSocketDisconnect:
        print("Status WebSocket disconnected")
    except Exception as e:
        print(f"Status WebSocket error: {e}")
