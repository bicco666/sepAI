from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import glob, asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

IDEAS, ORDERS = [], []

class Idea(BaseModel):
    id: str; asset: str="SOL"; chain:str="solana"; amount:float=0.1; risk:int=3; state:str="NEW"

@app.get("/healthz")
def healthz(): return {"status":"ok","ts":datetime.utcnow().isoformat()}

@app.get("/api/v1/ideas")
def list_ideas(limit:int=20, order:str="desc"):
    items = list(reversed(IDEAS))[:limit] if order=="desc" else IDEAS[:limit]
    return {"items": items}

@app.post("/api/v1/ideas/generate")
def gen_idea(body:dict):
    iid=f"idea_{len(IDEAS)+1}"; i=Idea(id=iid, asset=body.get("asset","SOL"), risk=int(body.get("risk",3)))
    IDEAS.append(i.model_dump()); return i

@app.post("/api/v1/ideas/{iid}/analyze")
def analyze(iid:str):
    i=next((x for x in IDEAS if x["id"]==iid), None)
    if not i: raise HTTPException(404,"idea not found")
    i.update({"side":"buy","hold_minutes":60,"state":"NEEDS_REVIEW"}); return i

@app.post("/api/v1/ideas/{iid}/to_orders")
def to_orders(iid:str):
    i=next((x for x in IDEAS if x["id"]==iid), None)
    if not i: raise HTTPException(404,"idea not found")
    o={"id":f"ord_{len(ORDERS)+1}","idea_id":iid,"asset":i["asset"],"amount":i["amount"],"state":"SCHEDULED"}
    ORDERS.append(o); return o

@app.get("/api/v1/wallet/balance")
def balance(): return {"balance": 123.45}

from backend.services.reporting import write_md

@app.post("/api/v1/tests/run/basic_flow")
def run_basic_flow():
    steps=[]
    try:
        i = gen_idea({"risk":3,"asset":"SOL"}); steps.append(f"idea {i.id} created")
        a = analyze(i.id); steps.append("analyzed ok")
        o = to_orders(i.id); steps.append(f"order {o['id']} scheduled")
        path = write_md("basic_flow", steps+["RESULT: OK"])
        return {"ok": True, "report_path": path}
    except Exception as e:
        path = write_md("basic_flow", steps+[f"RESULT: FAIL {e}"])
        raise HTTPException(500, detail=f"Report: {path}")

@app.on_event("startup")
async def _startup_smoke():
    try: run_basic_flow()
    except: pass

@app.get("/api/v1/tests/last_report")
def last_report():
    files = sorted(glob.glob("reports/*basic_flow*.md"))
    if not files: return {"found": False}
    p = files[-1]; content = open(p, "r", encoding="utf-8").read()
    ok = "RESULT: OK" in content
    return {"found": True, "ok": ok, "report_path": p}