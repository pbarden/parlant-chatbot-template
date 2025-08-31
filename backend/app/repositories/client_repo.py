from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.client import Client

class ClientRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str) -> Client | None:
        return self.db.query(Client).filter(Client.slug == slug).one_or_none()

    def create(self, *, slug: str, name: str, parlant_base_url: str | None, openai_api_key: str | None, config: dict | None) -> Client:
        c = Client(slug=slug, name=name, parlant_base_url=parlant_base_url, openai_api_key=openai_api_key, config=config)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c