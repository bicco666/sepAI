from typing import List, Optional
from fastapi import APIRouter

from src.store import trades_store
from src.models import Trade
from pydantic import BaseModel, Field
from fastapi import HTTPException

from src.execution.adapter import ExecutionAdapter


class ExecuteRequest(BaseModel):
    action: str = Field(example="AIRDROP")
    address: str = Field(example="So1anaEXAMPLEaddre55...............1234")
    amount: float = Field(gt=0, example=0.5)


router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/recent", summary="Recent trades", response_model=List[Trade])
async def recent_trades(limit: int = 20, status: Optional[str] = None) -> List[Trade]:
    data = trades_store
    if status:
        data = [t for t in data if (t.get("status") or '').upper() == status.upper()]
    # sort by executed_at desc if available
    try:
        data = sorted(data, key=lambda x: x.get("executed_at"), reverse=True)
    except Exception:
        pass
    return data[: max(1, min(limit, 200))]


@router.post("/execute", summary="Execute a trade or action")
async def execute(payload: ExecuteRequest):
    # only AIRDROP implemented for now
    if payload.action.upper() != "AIRDROP":
        raise HTTPException(status_code=400, detail="Only AIRDROP action supported in dev mode")
    adapter = ExecutionAdapter(mode="dev")
    try:
        trade = await adapter.execute_airdrop(payload.address, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return trade
