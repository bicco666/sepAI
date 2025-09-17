from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import time, itertools, random

router = APIRouter()
_TRADES: List[Dict[str, Any]] = []
_trade_id_counter = itertools.count(1)

@router.get("/recent")
def get_recent_trades(limit: int = 20):
    """Get recent trades"""
    sorted_trades = sorted(_TRADES, key=lambda x: x.get("executed_at", 0), reverse=True)
    return sorted_trades[:limit]

@router.post("/execute")
def execute_trade(
    action: str,
    asset: str,
    amount: float,
    address: Optional[str] = None,
    price: Optional[float] = None,
    live: bool = False
):
    """Execute a trade"""
    if action not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Action must be BUY or SELL")

    trade = {
        "id": f"trade_{next(_trade_id_counter):05d}",
        "executed_at": time.time(),
        "action": action,
        "asset": asset,
        "quantity": amount,
        "price": price or round(random.uniform(0.1, 10), 4),
        "address": address or "SimulatedAddress123",
        "status": "EXECUTED" if live else "SIMULATED",
        "live": live,
        "pnl": round(random.uniform(-0.01, 0.02), 4) if action == "SELL" else 0,
        "duration": f"{random.randint(1, 60)}m" if live else None
    }

    _TRADES.append(trade)

    return {
        "id": trade["id"],
        "status": trade["status"],
        "executed_at": trade["executed_at"],
        "action": action,
        "asset": asset,
        "quantity": amount
    }

@router.get("/{trade_id}")
def get_trade(trade_id: str):
    """Get specific trade details"""
    trade = next((t for t in _TRADES if t["id"] == trade_id), None)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

# Initialize with some sample trades
def _init_sample_trades():
    """Initialize with sample trades for demo purposes"""
    sample_trades = [
        {
            "id": f"trade_{next(_trade_id_counter):05d}",
            "executed_at": time.time() - 3600,  # 1 hour ago
            "action": "BUY",
            "asset": "SOL",
            "quantity": 0.5,
            "price": 1.234,
            "address": "DemoAddress123",
            "status": "EXECUTED",
            "live": True,
            "pnl": 0,
            "duration": "30m"
        },
        {
            "id": f"trade_{next(_trade_id_counter):05d}",
            "executed_at": time.time() - 1800,  # 30 min ago
            "action": "SELL",
            "asset": "JUP",
            "quantity": 10.0,
            "price": 0.056,
            "address": "DemoAddress456",
            "status": "EXECUTED",
            "live": True,
            "pnl": 0.0002,
            "duration": "15m"
        }
    ]

    _TRADES.extend(sample_trades)

# Initialize sample data
_init_sample_trades()