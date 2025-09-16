from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.store import trades_store, wallet_store
from src.models import TradeAction, Trade, TradeStatus


class ExecutionAdapter:
    """Simple Execution Adapter that can simulate actions.

    For dev: supports AIRDROP (credit wallet) and simple BUY/SELL simulation.
    """

    def __init__(self, mode: str = "dev"):
        self.mode = mode

    async def execute_airdrop(self, address: str, amount: float) -> dict:
        # simulate increasing the wallet balance
        w = wallet_store.get(address)
        if not w:
            raise ValueError("Wallet not found")
        w["balance_sol"] = w.get("balance_sol", 0.0) + amount
        w["timestamp"] = datetime.now(timezone.utc)

        trade = {
            "id": str(uuid4()),
            "strategy_id": "airdrop",
            "action": TradeAction.AIRDROP,
            "asset": "SOL",
            "quantity": amount,
            "price": None,
            "pnl": 0.0,
            "status": TradeStatus.CLOSED,
            "executed_at": datetime.now(timezone.utc),
            "duration": "00:00:01",
        }
        trades_store.insert(0, trade)
        return trade
