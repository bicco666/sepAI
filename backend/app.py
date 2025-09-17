from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uuid, os

from backend.services.reporting import write_report, latest_report

app = FastAPI(title="sepAI System Test API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.getenv("FRONTEND_DIR", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
def root_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

IDEAS: List[Dict[str, Any]] = []
ORDERS: List[Dict[str, Any]] = []
HISTORY: List[Dict[str, Any]] = []

class IdeaIn(BaseModel):
    asset: str = "SOL"
    chain: str = "solana"
    amount: float = 0.1
    risk: int = 3

def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

@app.get("/healthz")
def healthz():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}

@app.get("/api/v1/wallet/balance")
def wallet_balance():
    # simple mock balance
    return {"balance": 123.45}

def wallet_transfer(chain: str, amount: float) -> dict:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    txid = f"{chain[:3]}-{uuid.uuid4().hex[:12]}"
    return {"ok": True, "chain": chain, "amount": float(amount), "txid": txid}

@app.get("/api/v1/ideas")
def list_ideas(limit: int = 20, order: str = "desc"):
    items = IDEAS[-limit:] if order == "desc" else IDEAS[:limit]
    return {"items": list(reversed(items)) if order == "desc" else items}

@app.get("/api/v1/orders")
def list_orders(limit: int = 20, order: str = "desc"):
    items = ORDERS[-limit:] if order == "desc" else ORDERS[:limit]
    return {"items": list(reversed(items)) if order == "desc" else items}

@app.get("/api/v1/history")
def list_history(limit: int = 50, order: str = "desc"):
    items = HISTORY[-limit:] if order == "desc" else HISTORY[:limit]
    return {"items": list(reversed(items)) if order == "desc" else items}

@app.post("/api/v1/ideas/generate")
def generate_idea(body: IdeaIn):
    idea = {
        "id": _uid("idea"),
        "asset": body.asset,
        "chain": body.chain,
        "amount": float(body.amount),
        "risk": int(body.risk),
        "state": "NEW",
        "ts": datetime.utcnow().isoformat(),
    }
    IDEAS.append(idea)
    HISTORY.append({"ts": idea["ts"], "actor": "Forschung", "event": "IDEA_NEW", "ref": idea["id"]})
    return idea

@app.post("/api/v1/ideas/{idea_id}/analyze")
def analyze_idea(idea_id: str):
    idea = next((x for x in IDEAS if x["id"] == idea_id), None)
    if not idea:
        raise HTTPException(404, "Idea not found")
    idea.update({"plan": {"side": "buy", "entry": "mock", "hold_minutes": 1}, "state": "NEEDS_REVIEW"})
    HISTORY.append({"ts": datetime.utcnow().isoformat(), "actor": "Analyse", "event": "PLAN_READY", "ref": idea_id})
    return idea

@app.post("/api/v1/ideas/{idea_id}/to_orders")
def schedule_order(idea_id: str):
    idea = next((x for x in IDEAS if x["id"] == idea_id), None)
    if not idea:
        raise HTTPException(404, "Idea not found")
    order = {
        "id": _uid("ord"),
        "idea_id": idea_id,
        "asset": idea["asset"],
        "chain": idea["chain"],
        "amount": idea["amount"],
        "state": "SCHEDULED",
        "ts": datetime.utcnow().isoformat(),
    }
    ORDERS.append(order)
    HISTORY.append({"ts": order["ts"], "actor": "Execution", "event": "ORDER_SCHEDULED", "ref": order["id"]})
    return order

@app.post("/api/v1/orders/{order_id}/execute")
def execute_order(order_id: str):
    order = next((x for x in ORDERS if x["id"] == order_id), None)
    if not order:
        raise HTTPException(404, "Order not found")
    try:
        tx = wallet_transfer(order["chain"], order["amount"])
    except Exception as e:
        order["state"] = "FAILED"
        HISTORY.append({"ts": datetime.utcnow().isoformat(), "actor": "Execution", "event": "ORDER_FAILED", "ref": order_id, "detail": str(e)})
        raise HTTPException(400, str(e))

    order.update({"state": "CLOSED", "txid": tx["txid"]})
    HISTORY.append({"ts": datetime.utcnow().isoformat(), "actor": "Execution", "event": "ORDER_EXECUTED", "ref": order_id, "txid": tx["txid"]})
    return {"ok": True, "order": order}

def quality_check(idea_id: str, order_id: str, txid: str) -> dict:
    missing = []
    idea = next((x for x in IDEAS if x["id"] == idea_id), None)
    order = next((x for x in ORDERS if x["id"] == order_id), None)
    if not idea: missing.append("idea")
    if not order: missing.append("order")
    if not txid: missing.append("txid")
    ok = len(missing) == 0 and order.get("state") == "CLOSED"
    HISTORY.append({"ts": datetime.utcnow().isoformat(), "actor": "Quality", "event": "QA_DONE", "ref": order_id, "ok": ok})
    return {"ok": ok, "missing": missing}

@app.post("/api/v1/system/run")
def system_run():
    steps = []
    try:
        i = generate_idea(IdeaIn())
        steps.append(f"Forschung: Idee {i['id']} erstellt ({i['asset']} on {i['chain']}, amount={i['amount']})")
        a = analyze_idea(i["id"])
        steps.append("Analyse: Plan erstellt (buy, hold 1m)")
        o = schedule_order(i["id"])
        steps.append(f"Execution: Auftrag {o['id']} geplant")
        ex = execute_order(o["id"])
        txid = ex["order"]["txid"]
        steps.append(f"Execution: Auftrag ausgeführt, txid={txid}")
        qa = quality_check(i["id"], o["id"], txid)
        steps.append(f"Quality: ok={qa['ok']} missing={qa['missing']}")
        verdict = "RESULT: OK" if qa["ok"] else "RESULT: FAIL"
        path = write_report("system_run", steps + [verdict])
        return {"ok": qa["ok"], "report_path": path, "steps": steps}
    except Exception as e:
        path = write_report("system_run", steps + [f"RESULT: FAIL ({e})"])
        raise HTTPException(500, f"System run failed. Report: {path}")

@app.get("/api/v1/reports/latest")
def get_latest_report():
    return latest_report()
