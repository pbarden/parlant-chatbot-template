from __future__ import annotations
from ..models.session import ChatSession
from ..repositories.event_repo import EventRepo

class AnalyticsService:
    def __init__(self, event_repo: EventRepo):
        self.events = event_repo

    def record_event(self, *, db_session: ChatSession, event: dict) -> None:
        kind = event.get("kind", "message")
        source = event.get("source", "ai_agent")
        offset = int(event.get("offset", 0) or 0)
        payload = event.get("data", {})
        self.events.add(session_id_fk=db_session.id, kind=kind, source=source, offset=offset, payload=payload)