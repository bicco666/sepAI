from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time, itertools, random

class GenerateRequest(BaseModel):
    risk: int = 3
    asset: str = "SOL"

router = APIRouter()
_IDEAS: List[Dict[str, Any]] = []
_id_counter = itertools.count(1)

@router.get("/")
@router.get("")
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
def generate_ideas(body: GenerateRequest):
    risk = body.risk
    asset = body.asset
    out = []
    for _ in range(1):
        idea = _synthesize_research(risk, 10)
        idea['asset'] = asset  # override asset
        idea = _synthesize_analysis(idea)
        _IDEAS.append(idea)
        out.append(idea)
    return out[0]

@router.post("/{iid}/analyze")
def analyze(iid: str):
    i = next((x for x in _IDEAS if x["id"] == iid), None)
    if not i: raise HTTPException(404, "idea not found")
    i.update({"side": "buy", "hold_minutes": 60, "state": "NEEDS_REVIEW"})
    return i

@router.post("/{iid}/to_orders")
def to_orders(iid: str):
    i = next((x for x in _IDEAS if x["id"] == iid), None)
    if not i: raise HTTPException(404, "idea not found")
    o = {"id": f"ord_{len(_IDEAS) + 1}", "idea_id": iid, "asset": i["asset"], "amount": i.get("amount", i["budget"]), "state": "SCHEDULED"}
    return o
