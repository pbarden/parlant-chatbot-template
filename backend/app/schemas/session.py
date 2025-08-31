from __future__ import annotations
from pydantic import BaseModel

class SessionCreate(BaseModel):
    agent_id: str
    user_id: str | None = None

class SessionOut(BaseModel):
    public_token: str
    session_id: str  # parlant session id
    user_id: str | None = None

class SessionResume(BaseModel):
    public_token: str