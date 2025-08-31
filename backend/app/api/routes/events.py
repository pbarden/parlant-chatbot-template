from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...api.deps import get_db
from ...repositories.session_repo import SessionRepo
from ...services.parlant_client import ParlantClient
from ...services.analytics import AnalyticsService
from ...repositories.event_repo import EventRepo
from ...schemas.event import SendMessage, EventOut

router = APIRouter(prefix="/public/events", tags=["public-events"])


def _resolve_session(db: Session, public_token: str):
    repo = SessionRepo(db)
    item = repo.get_by_public(public_token)
    if not item:
        raise HTTPException(status_code=404, detail="session_not_found")
    return item


@router.post("/send/{public_token}")
async def send_message(public_token: str, payload: SendMessage, db: Session = Depends(get_db)):
    sess = _resolve_session(db, public_token)
    parlant = ParlantClient(base_url=sess.client.parlant_base_url)
    result = await parlant.post_event(session_id=sess.parlant_session_id, kind="message", source="customer", message=payload.message)
    return {"ok": True, "result": result}


@router.get("/stream/{public_token}", response_model=list[EventOut])
async def stream_events(public_token: str, min_offset: int = Query(0), db: Session = Depends(get_db)):
    sess = _resolve_session(db, public_token)
    parlant = ParlantClient(base_url=sess.client.parlant_base_url)

    events = await parlant.list_events(session_id=sess.parlant_session_id, min_offset=min_offset, kinds=["message", "status"], wait_for_data=30)

    # Persist analytics for each event and update offset
    ev_repo = EventRepo(db)
    analytics = AnalyticsService(ev_repo)
    max_offset = min_offset
    out: list[EventOut] = []
    for ev in events:
        if isinstance(ev, dict) and ev.get("kind") in {"message", "status"}:
            offset = int(ev.get("offset", 0) or 0)
            max_offset = max(max_offset, offset + 1)
            analytics.record_event(db_session=sess, event=ev)
            out.append(EventOut(kind=ev.get("kind", "message"), source=ev.get("source", "ai_agent"), offset=offset, data=ev.get("data")))
    if max_offset > min_offset:
        repo = SessionRepo(db)
        repo.update_offset(session=sess, offset=max_offset)
    return out