from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.store import trades_store, wallet_store
from src.models import TradeAction, Trade, TradeStatus
from src.execution.solana_client import SolanaClient
import os


class ExecutionAdapter:
    """Simple Execution Adapter that can simulate actions.

    For dev: supports AIRDROP (credit wallet) and simple BUY/SELL simulation.
    """

    def __init__(self, mode: str = "dev"):
        self.mode = mode
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "")
        self.allow_mainnet = os.getenv("ALLOW_MAINNET_TRANSACTIONS", "").lower() in ("1", "true", "yes")
        self._sol = None
        if self.rpc_url:
            self._sol = SolanaClient(rpc_url=self.rpc_url)

    async def execute_airdrop(self, address: str, amount: float) -> dict:
        # If RPC is configured and not mainnet-blocked, attempt a real airdrop (devnet/testnet)
        if self._sol and not self.allow_mainnet:
            try:
                lamports = int(amount * 1_000_000_000)
                await self._sol.request_airdrop(address, lamports)
            except Exception:
                # fall back to simulation if RPC fails
                pass
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

    async def execute_buy(self, address: str, asset: str, quantity: float, price: float) -> dict:
        # simple simulation: deduct cost from wallet (price * quantity)
        w = wallet_store.get(address)
        if not w:
            raise ValueError("Wallet not found")
        cost = price * quantity
        if w.get("balance_sol", 0.0) < cost:
            raise ValueError("Insufficient funds")
        w["balance_sol"] = w.get("balance_sol", 0.0) - cost
        w["timestamp"] = datetime.now(timezone.utc)

        trade = {
            "id": str(uuid4()),
            "strategy_id": "buy",
            "action": TradeAction.BUY,
            "asset": asset,
            "quantity": quantity,
            "price": price,
            "pnl": 0.0,
            "status": TradeStatus.CLOSED,
            "executed_at": datetime.now(timezone.utc),
            "duration": "00:00:02",
        }
        trades_store.insert(0, trade)
        return trade

    async def execute_sell(self, address: str, asset: str, quantity: float, price: float) -> dict:
        # simple simulation: credit proceeds to wallet
        w = wallet_store.get(address)
        if not w:
            raise ValueError("Wallet not found")
        proceeds = price * quantity
        w["balance_sol"] = w.get("balance_sol", 0.0) + proceeds
        w["timestamp"] = datetime.now(timezone.utc)

        trade = {
            "id": str(uuid4()),
            "strategy_id": "sell",
            "action": TradeAction.SELL,
            "asset": asset,
            "quantity": quantity,
            "price": price,
            "pnl": 0.0,
            "status": TradeStatus.CLOSED,
            "executed_at": datetime.now(timezone.utc),
            "duration": "00:00:02",
        }
        trades_store.insert(0, trade)
        return trade
