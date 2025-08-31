from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.event import ChatEvent

class EventRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, *, session_id_fk: int, kind: str, source: str, offset: int, payload: dict) -> ChatEvent:
        ev = ChatEvent(session_id_fk=session_id_fk, kind=kind, source=source, offset=offset, payload=payload)
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev