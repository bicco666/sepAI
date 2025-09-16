from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.store import ideas_store
from src.bus import bus
from src.models import IdeaStatus, Idea


router = APIRouter(prefix="/ideas", tags=["ideas"])


class IdeaCreate(BaseModel):
    source: str = Field(example="research")
    asset: str = Field(example="SOL")
    type: str = Field(example="yield")
    risk: int = Field(ge=1, le=5, example=3)
    budget: float = Field(gt=0, example=0.5)
    ttl: Optional[int] = Field(default=5400, description="seconds")


@router.get("", summary="List all ideas", response_model=List[Idea])
async def list_ideas(status: Optional[IdeaStatus] = None, limit: int = 50) -> List[Idea]:
    data = ideas_store
    if status is not None:
        data = [i for i in data if i.get("status") == status]
    return data[: max(1, min(limit, 200))]


@router.post("", summary="Create a new idea", response_model=Idea)
async def create_idea(payload: IdeaCreate) -> Idea:
    idea = {
        "id": str(uuid4()),
        "source": payload.source,
        "asset": payload.asset,
        "type": payload.type,
        "risk": payload.risk,
        "budget": payload.budget,
        "status": IdeaStatus.NEW,
        "created_at": datetime.now(timezone.utc),
        "ttl": payload.ttl if payload.ttl is not None else 5400,
    }
    ideas_store.insert(0, idea)
    # Publish to event bus (Redis or in-memory fallback)
    await bus.publish("idea_stream", {
        "idea_id": idea["id"],
        "source": idea["source"],
        "asset": idea["asset"],
        "type": idea["type"],
        "risk": idea["risk"],
        "budget": idea["budget"],
        "ttl": idea["ttl"],
        "created_at": idea["created_at"].isoformat(),
    })
    return idea


def _get_idea(idea_id: str) -> Optional[dict]:
    for it in ideas_store:
        if it.get("id") == idea_id:
            return it
    return None


_ALLOWED = {
    IdeaStatus.NEW: {IdeaStatus.NEEDS_REVIEW, IdeaStatus.CANCELLED},
    IdeaStatus.NEEDS_REVIEW: {IdeaStatus.READY_FOR_QA, IdeaStatus.CANCELLED},
    IdeaStatus.READY_FOR_QA: {IdeaStatus.APPROVED, IdeaStatus.CANCELLED},
    IdeaStatus.APPROVED: {IdeaStatus.SCHEDULED, IdeaStatus.CANCELLED},
    IdeaStatus.SCHEDULED: set(),
    IdeaStatus.CANCELLED: set(),
}


def _transition(idea: dict, to_state: IdeaStatus) -> dict:
    cur = idea.get("status")
    if to_state not in _ALLOWED.get(cur, set()):
        raise HTTPException(status_code=400, detail=f"Illegal transition {cur} -> {to_state}")
    idea["status"] = to_state
    return idea


@router.post("/{idea_id}/review", summary="Mark idea as NEEDS_REVIEW", response_model=Idea)
async def mark_review(idea_id: str) -> Idea:
    idea = _get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return _transition(idea, IdeaStatus.NEEDS_REVIEW)


@router.post("/{idea_id}/qa-ready", summary="Mark idea as READY_FOR_QA", response_model=Idea)
async def mark_qa_ready(idea_id: str) -> Idea:
    idea = _get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return _transition(idea, IdeaStatus.READY_FOR_QA)


@router.post("/{idea_id}/approve", summary="Approve idea", response_model=Idea)
async def approve(idea_id: str) -> Idea:
    idea = _get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return _transition(idea, IdeaStatus.APPROVED)


@router.post("/{idea_id}/schedule", summary="Schedule idea", response_model=Idea)
async def schedule(idea_id: str) -> Idea:
    idea = _get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return _transition(idea, IdeaStatus.SCHEDULED)


@router.post("/{idea_id}/cancel", summary="Cancel idea", response_model=Idea)
async def cancel(idea_id: str) -> Idea:
    idea = _get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea["status"] = IdeaStatus.CANCELLED
    return idea
