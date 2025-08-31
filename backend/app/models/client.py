from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, func, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base import Base

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # External configuration per tenant
    parlant_base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    openai_api_key: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Arbitrary JSON config flags (routing, UI tweaks, etc.)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())