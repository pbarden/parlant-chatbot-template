from __future__ import annotations
from pydantic import BaseModel

class SendMessage(BaseModel):
    message: str

class EventOut(BaseModel):
    kind: str
    source: str
    offset: int | None = None
    data: dict | None = None