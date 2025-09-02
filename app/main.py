from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, sessions, npc, websocket

app = FastAPI(title="NPC Game Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(npc.router, prefix="/npc", tags=["NPC"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "NPC Game backend running 🚀"}
