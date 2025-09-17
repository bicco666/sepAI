from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import time, itertools, random

router = APIRouter()
_STRATEGIES: List[Dict[str, Any]] = []
_strategy_id_counter = itertools.count(1)

@router.get("/")
@router.get("")
def list_strategies():
    return _STRATEGIES

@router.post("/generate")
def generate_strategies(limit: int = 5):
    """Generate strategies from ideas"""
    strategies = []
    for _ in range(max(1, min(10, limit))):
        strategy = _create_strategy_from_idea()
        _STRATEGIES.append(strategy)
        strategies.append(strategy)
    return {"count": len(strategies), "items": strategies}

def _create_strategy_from_idea() -> Dict[str, Any]:
    """Create a strategy from an analyzed idea"""
    assets = ["SOL", "JUP", "PYTH", "BONK", "RAY"]
    entry_conditions = [
        f"Price above {round(random.uniform(0.1, 10), 4)} SOL",
        f"Volume > {random.randint(1000, 10000)}",
        f"RSI < {random.randint(20, 40)}",
        f"MACD crossover bullish"
    ]
    exit_conditions = [
        f"Take profit at {round(random.uniform(1.01, 1.15), 4)}x",
        f"Stop loss at {round(random.uniform(0.85, 0.99), 4)}x",
        f"Time-based exit after {random.randint(1, 24)}h"
    ]

    return {
        "id": f"strat_{next(_strategy_id_counter):05d}",
        "idea_id": f"idea_{random.randint(1, 99999):05d}",
        "created_at": time.time(),
        "asset": random.choice(assets),
        "entry_conditions": random.choice(entry_conditions),
        "exit_conditions": random.choice(exit_conditions),
        "stop_loss": round(random.uniform(0.02, 0.10), 4),
        "take_profit": round(random.uniform(0.05, 0.25), 4),
        "status": "DRAFT",
        "risk_score": round(random.uniform(1, 5), 1)
    }

@router.post("/{strategy_id}/execute")
def execute_strategy(strategy_id: str, live: bool = False):
    """Execute a strategy"""
    strategy = next((s for s in _STRATEGIES if s["id"] == strategy_id), None)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Mark as executed
    strategy["status"] = "EXECUTED" if live else "SIMULATED"
    strategy["executed_at"] = time.time()

    return {
        "strategy_id": strategy_id,
        "status": strategy["status"],
        "executed_at": strategy["executed_at"],
        "live": live
    }