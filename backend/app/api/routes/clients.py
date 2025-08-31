from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...schemas.client import ClientCreate, ClientOut
from ...repositories.client_repo import ClientRepo
from ...api.deps import get_db

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/", response_model=ClientOut)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    repo = ClientRepo(db)
    created = repo.create(
        slug=payload.slug,
        name=payload.name,
        parlant_base_url=payload.parlant_base_url,
        openai_api_key=payload.openai_api_key,
        config=payload.config,
    )
    return created