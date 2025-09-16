import os
from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)) -> bool:
    """Require API key only if `API_KEY` env var is set.

    If `API_KEY` is unset or empty, no check is enforced (convenience for local dev/tests).
    """
    expected = os.getenv("API_KEY", "")
    if not expected:
        return True
    if x_api_key is None or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True
