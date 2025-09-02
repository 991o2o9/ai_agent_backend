from fastapi import FastAPI
from app.api import users, sessions, npc

app = FastAPI(title="NPC Game Backend")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(npc.router, prefix="/npc", tags=["NPC"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "NPC Game backend running 🚀"}
