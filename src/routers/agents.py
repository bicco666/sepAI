from typing import List, Optional
from fastapi import APIRouter, HTTPException

from src.store import agents_store, ideas_store
from src.agents.research import generate_research_ideas


router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", summary="Agent status and versions")
async def agents_status() -> List[dict]:
    return agents_store


@router.post("/research/generate", summary="Trigger research agent to generate ideas")
async def trigger_research(time_value: int = 30, time_unit: Optional[str] = "minutes", risk_pref: int = 3, live: bool = False):
    try:
        ideas = await generate_research_ideas(time_value=time_value, time_unit=time_unit, risk_pref=risk_pref, live=live)
        # insert into ideas_store for visibility
        for i in ideas:
            ideas_store.insert(0, i)
        return {"count": len(ideas), "ideas": ideas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

