from __future__ import annotations
import httpx
from typing import Iterable
from ..core.config import settings

class ParlantClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.PARLANT_BASE_URL or "http://localhost:8800").rstrip("/")
        self.timeout = timeout or settings.HTTP_CLIENT_TIMEOUT_S
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def close(self):
        await self._client.aclose()

    async def create_session(self, *, agent_id: str, customer_id: str | None, title: str | None = None) -> dict:
        payload = {"agent_id": agent_id}
        if customer_id:
            payload["customer_id"] = customer_id
        if title:
            payload["title"] = title
        r = await self._client.post("/sessions/", json=payload)
        r.raise_for_status()
        return r.json()

    async def post_event(self, *, session_id: str, kind: str, source: str, message: str) -> dict:
        payload = {"kind": kind, "source": source, "message": message}
        r = await self._client.post(f"/sessions/{session_id}/events", json=payload)
        r.raise_for_status()
        return r.json()

    async def list_events(self, *, session_id: str, min_offset: int = 0, kinds: Iterable[str] | None = None, wait_for_data: int | None = 30) -> list[dict]:
        params: dict[str, str] = {"min_offset": str(min_offset)}
        if kinds:
            params["kinds"] = ",".join(kinds)
        if wait_for_data is not None:
            params["wait_for_data"] = str(wait_for_data)
        r = await self._client.get(f"/sessions/{session_id}/events", params=params)
        r.raise_for_status()
        return r.json()