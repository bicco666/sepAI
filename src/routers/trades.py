from typing import List, Optional
from fastapi import APIRouter

from src.store import trades_store
from src.models import Trade
from pydantic import BaseModel, Field
from fastapi import HTTPException, Depends

from src.execution.adapter import ExecutionAdapter
from src.models import Trade as TradeModel
from src.auth import require_api_key


class ExecuteRequest(BaseModel):
    action: str = Field(example="AIRDROP")
    address: str = Field(example="So1anaEXAMPLEaddre55...............1234")
    amount: float = Field(gt=0, example=0.5)
    asset: Optional[str] = Field(default="SOL")
    price: Optional[float] = Field(default=None)
    live: Optional[bool] = Field(default=False, description="If true and SOLANA_RPC_URL is configured, attempt real RPC calls (devnet/testnet). Mainnet only if ALLOW_MAINNET_TRANSACTIONS is set")


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


@router.post("/execute", summary="Execute a trade or action", response_model=TradeModel)
async def execute(payload: ExecuteRequest, _=Depends(require_api_key)):
    # only AIRDROP implemented for now
    adapter = ExecutionAdapter(mode="dev")
    act = payload.action.upper()
    try:
        if act == "AIRDROP":
            trade = await adapter.execute_airdrop(payload.address, payload.amount)
        elif act == "BUY":
            if payload.price is None:
                raise HTTPException(status_code=400, detail="price required for BUY")
            trade = await adapter.execute_buy(payload.address, payload.asset or "SOL", payload.amount, payload.price)
        elif act == "SELL":
            if payload.price is None:
                raise HTTPException(status_code=400, detail="price required for SELL")
            trade = await adapter.execute_sell(payload.address, payload.asset or "SOL", payload.amount, payload.price)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action: {payload.action}")
    except ValueError as e:
        # map to 400 for insufficient funds, 404 for wallet not found
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    return trade
