from typing import List
from fastapi import APIRouter

from src.store import strategies_store


router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("", summary="List strategies")
async def list_strategies() -> List[dict]:
    return strategies_store

