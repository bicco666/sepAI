from __future__ import annotations

from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from src.store import ideas_store, strategies_store
from src.models import Strategy, StrategyStatus
from src.bus import bus


def _risk_to_params(risk: int) -> Dict[str, float]:
    # Simple mapping from risk 1..5 to stop_loss and take_profit multipliers / max_dd
    mapping = {
        1: {"stop_loss": 0.01, "take_profit": 0.02, "max_dd": 0.04},
        2: {"stop_loss": 0.02, "take_profit": 0.04, "max_dd": 0.06},
        3: {"stop_loss": 0.03, "take_profit": 0.06, "max_dd": 0.08},
        4: {"stop_loss": 0.04, "take_profit": 0.08, "max_dd": 0.1},
        5: {"stop_loss": 0.05, "take_profit": 0.12, "max_dd": 0.12},
    }
    return mapping.get(max(1, min(5, risk)), mapping[3])


async def generate_strategies_from_ideas(limit: int = 10, only_status: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Generate strategy drafts from recent ideas.

    - Picks ideas from `ideas_store` matching `only_status` (if provided) or default NEW/NEEDS_REVIEW.
    - Creates Strategy drafts and inserts into `strategies_store`.
    - Publishes to `strategy_stream` on the bus.
    Returns list of created strategy dicts.
    """
    if only_status is None:
        only_status = ["NEW", "NEEDS_REVIEW"]

    created: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    candidates = [i for i in ideas_store if i.get("status") in only_status]
    # sort by created_at desc if available
    try:
        candidates = sorted(candidates, key=lambda x: x.get("created_at") or now, reverse=True)
    except Exception:
        pass

    for idea in candidates[:limit]:
        params = _risk_to_params(int(idea.get("risk", 3)))
        strat = {
            "id": str(uuid4()),
            "idea_id": idea.get("id"),
            "entry_conditions": f"enter when price breaks X on {idea.get('asset')}",
            "exit_conditions": f"exit when target reached or stop loss hit",
            "stop_loss": params["stop_loss"],
            "take_profit": params["take_profit"],
            "max_dd": params["max_dd"],
            "status": StrategyStatus.DRAFT,
        }
        strategies_store.insert(0, strat)
        # publish lightweight strategy to bus
        await bus.publish("strategy_stream", {
            "strategy_id": strat["id"],
            "idea_id": strat["idea_id"],
            "asset": idea.get("asset"),
            "stop_loss": strat["stop_loss"],
            "take_profit": strat["take_profit"],
            "created_at": now.isoformat(),
        })
        created.append(strat)

    return created
