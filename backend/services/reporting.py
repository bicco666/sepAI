from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
import glob

router = APIRouter()

REPORTS = Path("reports"); REPORTS.mkdir(exist_ok=True)
def write_md(name:str, lines:list[str])->str:
    p = REPORTS / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{name}.md"
    p.write_text("# "+name+"\n\n"+ "\n".join(f"- {l}" for l in lines), encoding="utf-8")
    return str(p)

# Import the functions from backend.app
from backend.app import run_basic_flow

@router.post("/run/basic_flow")
def run_basic_flow_endpoint():
    return run_basic_flow()

@router.get("/last_report")
def last_report():
    files = sorted(glob.glob("reports/*basic_flow*.md"))
    if not files: return {"found": False}
    p = files[-1]; content = open(p, "r", encoding="utf-8").read()
    ok = "RESULT: OK" in content
    return {"found": True, "ok": ok, "report_path": p}