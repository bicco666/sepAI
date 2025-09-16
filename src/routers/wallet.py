from fastapi import APIRouter, HTTPException
from src.models import WalletBalance
from datetime import datetime, timezone

router = APIRouter(prefix="/wallet", tags=["wallet"])

# Mock wallet address
WALLET_ADDRESS = "So1anaEXAMPLEaddre55...............1234"

@router.get("/balance", response_model=WalletBalance)
async def get_wallet_balance(address: str = WALLET_ADDRESS):
    # Mock implementation - in production, integrate with Solana RPC
    if address != WALLET_ADDRESS:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletBalance(
        address=address,
        balance_sol=1.0000,  # Demo value
        timestamp=datetime.now(timezone.utc)
    )
