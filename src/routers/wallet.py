from fastapi import APIRouter, HTTPException
from src.models import WalletBalance
from datetime import datetime, timezone
from src.store import wallet_store

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/balance", response_model=WalletBalance)
async def get_wallet_balance(address: str):
    w = wallet_store.get(address)
    if not w:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletBalance(
        address=w["address"],
        balance_sol=w.get("balance_sol", 0.0),
        timestamp=w.get("timestamp", datetime.now(timezone.utc)),
    )


@router.post("/update", summary="Dev: update wallet balance")
async def update_wallet_balance(address: str, balance_sol: float):
    w = wallet_store.get(address)
    if not w:
        raise HTTPException(status_code=404, detail="Wallet not found")
    w["balance_sol"] = balance_sol
    w["timestamp"] = datetime.now(timezone.utc)
    return {"address": address, "balance_sol": balance_sol}
