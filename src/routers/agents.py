from typing import List
from fastapi import APIRouter

from src.store import agents_store


router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", summary="Agent status and versions")
async def agents_status() -> List[dict]:
    return agents_store

