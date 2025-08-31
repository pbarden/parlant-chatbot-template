from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)

    user_id: Mapped[str | None] = mapped_column(String(128), index=True)

    # Parlant identifiers
    agent_id: Mapped[str] = mapped_column(String(128), index=True)
    parlant_session_id: Mapped[str] = mapped_column(String(128), index=True)

    # Public token to expose to browsers
    public_token: Mapped[str] = mapped_column(String(512), unique=True, index=True)

    last_offset: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client")

    __table_args__ = (
        UniqueConstraint("client_id", "user_id", "agent_id", name="uq_client_user_agent"),
    )