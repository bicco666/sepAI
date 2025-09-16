from typing import List, Optional
from fastapi import APIRouter, HTTPException

from src.store import strategies_store
from src.agents.analysis import generate_strategies_from_ideas


router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("", summary="List strategies")
async def list_strategies() -> List[dict]:
    return strategies_store


@router.post("/generate", summary="Trigger analysis agent to generate strategies from ideas")
async def trigger_analysis(limit: int = 10, only_status: Optional[str] = None):
    try:
        statuses = None
        if only_status:
            statuses = [s.strip().upper() for s in only_status.split(',') if s.strip()]
        created = await generate_strategies_from_ideas(limit=limit, only_status=statuses)
        return {"count": len(created), "strategies": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

