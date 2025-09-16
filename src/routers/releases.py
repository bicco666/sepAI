from typing import List
from uuid import uuid4
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.store import releases_store


router = APIRouter(prefix="/releases", tags=["releases"])


class ReleaseCreate(BaseModel):
    targets: List[str] = Field(example=["Forschung", "Analyse"])
    version: str = Field(example="1.2.4")
    notes: str = Field(example="Minor improvements and fixes")


@router.get("", summary="List releases")
async def list_releases() -> List[dict]:
    return releases_store


@router.post("", summary="Create a release")
async def create_release(payload: ReleaseCreate) -> dict:
    release = {
        "id": str(uuid4()),
        "targets": payload.targets,
        "version": payload.version,
        "notes": payload.notes,
        "status": "DRAFT",
    }
    releases_store.insert(0, release)
    return release

