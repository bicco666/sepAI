from fastapi import APIRouter
from typing import List, Dict, Any
import time, itertools, random

router = APIRouter()
_IDEAS: List[Dict[str, Any]] = []
_id_counter = itertools.count(1)

@router.get("/")
def list_ideas():
    return _IDEAS

def _synthesize_research(risk: int, minutes: int) -> Dict[str, Any]:
    assets = ["SOL", "JUP", "PYTH", "BONK"]
    strategies = ["MeanReversion", "Momentum", "Arb", "Breakout"]
    return {
        "id": f"idea_{next(_id_counter):05d}",
        "created_at": time.time(),
        "source": "Research",
        "asset": random.choice(assets),
        "type": random.choice(strategies),
        "budget": round(5 + risk * 2.5, 2),
        "risk": risk,
        "status": "NEW",
    }

def _synthesize_analysis(idea: Dict[str, Any]) -> Dict[str, Any]:
    idea = dict(idea)
    idea["status"] = "ANALYZED"
    idea["score"] = round(0.4 + 0.6 * random.random(), 2)
    return idea

@router.post("/generate")
def generate_ideas(limit: int = 3, risk: int = 3, minutes: int = 10):
    out = []
    for _ in range(max(1, min(10, limit))):
        idea = _synthesize_research(risk, minutes)
        idea = _synthesize_analysis(idea)
        _IDEAS.append(idea)
        out.append(idea)
    return {"count": len(out), "items": out}
