from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class ChatEvent(Base):
    __tablename__ = "chat_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    session_id_fk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(32))  # message|status
    source: Mapped[str] = mapped_column(String(64))  # customer|ai_agent|human_agent
    offset: Mapped[int] = mapped_column(Integer, default=0)

    payload: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession")