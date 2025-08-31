from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.session import ChatSession

class SessionRepo:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id_: int) -> ChatSession | None:
        return self.db.get(ChatSession, id_)

    def get_by_public(self, token: str) -> ChatSession | None:
        return self.db.query(ChatSession).filter(ChatSession.public_token == token).one_or_none()

    def upsert(self, *, client_id: int, user_id: str | None, agent_id: str, parlant_session_id: str, public_token: str) -> ChatSession:
        existing = (
            self.db.query(ChatSession)
            .filter(ChatSession.client_id == client_id, ChatSession.user_id == user_id, ChatSession.agent_id == agent_id)
            .one_or_none()
        )
        if existing:
            existing.parlant_session_id = parlant_session_id
            existing.public_token = public_token
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        item = ChatSession(
            client_id=client_id,
            user_id=user_id,
            agent_id=agent_id,
            parlant_session_id=parlant_session_id,
            public_token=public_token,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_offset(self, *, session: ChatSession, offset: int) -> None:
        session.last_offset = max(session.last_offset or 0, offset)
        self.db.add(session)
        self.db.commit()