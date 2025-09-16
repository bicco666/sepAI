from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List, Dict
from uuid import uuid4

# Simple in-memory stores for demo purposes

ideas_store: List[Dict] = []
strategies_store: List[Dict] = []
trades_store: List[Dict] = []
wallet_store: Dict[str, Dict] = {}
agents_store: List[Dict] = [
    {"name": "Quality", "version": "1.2.3", "status": "OK"},
    {"name": "Forschung", "version": "1.2.3", "status": "OK"},
    {"name": "Analyse", "version": "1.2.3", "status": "OK"},
    {"name": "Execution", "version": "1.2.3", "status": "OK"},
]
releases_store: List[Dict] = []


def seed_demo_data():
    if trades_store:
        return
    now = datetime.now(timezone.utc)
    samples = [
        {
            "id": str(uuid4()),
            "strategy_id": "demo-strat-1",
            "action": "BUY",
            "asset": "SOL",
            "quantity": 0.5,
            "price": 150.0,
            "pnl": 0.0002,
            "status": "CLOSED",
            "executed_at": now - timedelta(minutes=1),
            "duration": "00:01:00",
        },
        {
            "id": str(uuid4()),
            "strategy_id": "demo-strat-2",
            "action": "SELL",
            "asset": "PUMP",
            "quantity": 0.1,
            "price": 0.01,
            "pnl": -0.0001,
            "status": "CLOSED",
            "executed_at": now - timedelta(minutes=3, seconds=30),
            "duration": "00:03:30",
        },
    ]
    trades_store.extend(samples)


def seed_wallet():
    # ensure a demo wallet exists
    if wallet_store:
        return
    wallet_store["So1anaEXAMPLEaddre55...............1234"] = {
        "address": "So1anaEXAMPLEaddre55...............1234",
        "balance_sol": 1.0,
        "timestamp": datetime.now(timezone.utc),
    }


seed_wallet()


seed_demo_data()

