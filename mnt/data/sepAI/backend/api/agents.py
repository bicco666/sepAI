from fastapi import APIRouter, HTTPException
import time

router = APIRouter()

@router.get("/status")
def status():
    return {
        "research": {"status": "OK", "version": "1.2.3"},
        "analysis": {"status": "OK", "version": "1.2.3"},
        "quality": {"status": "OK", "version": "1.2.3"},
        "execution": {"status": "OK", "version": "1.2.3"},
    }

@router.post("/research/generate")
def research_generate(time_value: int = 10, time_unit: str = "minutes", risk_pref: int = 3, live: bool = False):
    try:
        from backend.api.ideas import generate_ideas  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ideas module unavailable: {e}")
    minutes = time_value if time_unit.startswith("min") else time_value * 60
    res = generate_ideas(limit=3, risk=risk_pref, minutes=minutes)  # type: ignore
    return res

@router.get("/health")
def agents_health():
    return {"module":"agents","ok":True,"ts":time.time()}
