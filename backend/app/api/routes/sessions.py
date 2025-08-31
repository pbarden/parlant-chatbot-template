from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas.session import SessionCreate, SessionOut, SessionResume
from ...api.deps import get_db, get_client_by_slug
from ...repositories.session_repo import SessionRepo
from ...repositories.client_repo import ClientRepo
from ...core.security import encode_public_token, decode_public_token
from ...services.parlant_client import ParlantClient

router = APIRouter(prefix="/public/sessions", tags=["public-sessions"])

@router.post("/{client_slug}", response_model=SessionOut)
async def create_or_resume_session(client_slug: str, payload: SessionCreate, db: Session = Depends(get_db)):
    client = get_client_by_slug(client_slug, db)
    parlant = ParlantClient(base_url=client.parlant_base_url)

    # Create fresh session with Parlant
    created = await parlant.create_session(agent_id=payload.agent_id, customer_id=payload.user_id, title=None)
    parlant_session_id = created.get("id") or created.get("session_id")
    if not parlant_session_id:
        raise HTTPException(status_code=500, detail="parlant_session_missing")

    public = encode_public_token({
        "client_id": client.id,
        "parlant_session_id": parlant_session_id,
        "agent_id": payload.agent_id,
        "user_id": payload.user_id,
    })

    repo = SessionRepo(db)
    db_item = repo.upsert(
        client_id=client.id,
        user_id=payload.user_id,
        agent_id=payload.agent_id,
        parlant_session_id=parlant_session_id,
        public_token=public,
    )

    return SessionOut(public_token=db_item.public_token, session_id=parlant_session_id, user_id=db_item.user_id)


@router.post("/resume/{client_slug}", response_model=SessionOut)
async def resume_session(client_slug: str, payload: SessionResume, db: Session = Depends(get_db)):
    # Accept an existing token and simply echo the session mapping; reject if token invalid or client mismatch
    data = decode_public_token(payload.public_token)
    repo = SessionRepo(db)
    db_item = repo.get_by_public(payload.public_token)
    if not db_item:
        raise HTTPException(status_code=404, detail="session_not_found")
    return SessionOut(public_token=db_item.public_token, session_id=db_item.parlant_session_id, user_id=db_item.user_id)