"""
api/auth.py

API key authentication middleware.
Keys are loaded from the environment variable ANALYSER_API_KEYS
as a comma-separated list.

In development, set ANALYSER_ENV=development to skip key enforcement.
"""

from __future__ import annotations

import os
import logging
from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)


def _load_api_keys() -> set[str]:
    raw = os.environ.get("ANALYSER_API_KEYS", "")
    keys = {k.strip() for k in raw.split(",") if k.strip()}
    if not keys:
        logger.warning(
            "ANALYSER_API_KEYS is not set. "
            "Set ANALYSER_ENV=development to disable auth for local development."
        )
    return keys


_API_KEYS: set[str] = _load_api_keys()
_DEV_MODE: bool = os.environ.get("ANALYSER_ENV", "").lower() == "development"


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    """
    FastAPI dependency. Raises 401 if the key is missing or invalid.
    Auth is bypassed entirely in development mode.
    """
    if _DEV_MODE:
        return

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    if x_api_key not in _API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
