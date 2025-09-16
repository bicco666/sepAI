from __future__ import annotations

import os
import json
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone

from src.bus import bus


async def fetch_coingecko_solana_tokens(limit: int = 10) -> List[Dict[str, Any]]:
    """Try to fetch Solana ecosystem tokens from CoinGecko if enabled.

    This is optional and only used when `ENABLE_INTERNET_RESEARCH` env var is truthy.
    """
    if not os.getenv("ENABLE_INTERNET_RESEARCH"):
        return []
    try:
        import httpx

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "category": "solana-ecosystem", "order": "market_cap_desc", "per_page": limit, "page": 1}
        r = httpx.get(url, params=params, timeout=10.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []


async def generate_research_ideas(time_value: int = 30, time_unit: str = "minutes", risk_pref: int = 3, live: bool = False) -> List[Dict[str, Any]]:
    """Generate ideas: Try live web research (CoinGecko) when allowed, otherwise fallback to heuristic list.

    Each idea is published to `idea_stream` on the event bus and also returned.
    """
    ideas: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    # Attempt live token discovery via CoinGecko
    tokens = []
    try:
        tokens = await fetch_coingecko_solana_tokens(limit=10)
    except Exception:
        tokens = []

    if tokens:
        for t in tokens:
            asset = t.get("symbol", "SOL").upper()
            idea = {
                "id": str(uuid4()),
                "source": "research",
                "asset": asset,
                "type": "short-term trade",
                "risk": min(max(risk_pref, 1), 5),
                "budget": 0.1,
                "status": "NEW",
                "created_at": now,
                "ttl": 3600,
            }
            ideas.append(idea)
    else:
        # fallback: static seeds tailored to Solana ecosystem
        seeds = ["SOL", "BONK", "JUP", "ORCA", "RAY", "PUMP"]
        for i, asset in enumerate(seeds):
            idea = {
                "id": str(uuid4()),
                "source": "research",
                "asset": asset,
                "type": "short-term trade" if i % 2 == 0 else "swing",
                "risk": min(max(risk_pref + (i % 3) - 1, 1), 5),
                "budget": 0.1 + (i * 0.05),
                "status": "NEW",
                "created_at": now,
                "ttl": 3600,
            }
            ideas.append(idea)

    # publish ideas to bus
    for idea in ideas:
        # publish lightweight payload
        await bus.publish("idea_stream", {
            "idea_id": idea["id"],
            "source": idea["source"],
            "asset": idea["asset"],
            "type": idea["type"],
            "risk": idea["risk"],
            "budget": idea["budget"],
            "created_at": idea["created_at"].isoformat(),
        })

    return ideas
