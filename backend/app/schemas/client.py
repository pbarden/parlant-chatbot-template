from __future__ import annotations
from pydantic import BaseModel, Field

class ClientCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=64)
    name: str
    parlant_base_url: str | None = None
    openai_api_key: str | None = None
    config: dict | None = None

class ClientOut(BaseModel):
    id: int
    slug: str
    name: str
    is_active: bool
    parlant_base_url: str | None
    config: dict | None

    class Config:
        from_attributes = True