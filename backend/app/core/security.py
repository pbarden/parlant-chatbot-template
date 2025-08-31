from __future__ import annotations
from itsdangerous import URLSafeSerializer, BadSignature
from typing import Any
from .config import settings

_serializer = URLSafeSerializer(settings.PUBLIC_TOKEN_SECRET, salt="public-session")


def encode_public_token(data: dict[str, Any]) -> str:
    return _serializer.dumps(data)


def decode_public_token(token: str) -> dict[str, Any]:
    try:
        return _serializer.loads(token)
    except BadSignature as e:
        raise ValueError("invalid token") from e