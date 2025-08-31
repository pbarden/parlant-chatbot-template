from __future__ import annotations
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..repositories.client_repo import ClientRepo


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client_by_slug(slug: str, db: Session = Depends(get_db)):
    repo = ClientRepo(db)
    client = repo.get_by_slug(slug)
    if not client or not client.is_active:
        raise HTTPException(status_code=404, detail="client_not_found")
    return client