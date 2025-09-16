from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import time

router = APIRouter()

def _import_solana_services():
    try:
        from backend.services.solana_client import get_balance, request_airdrop  # type: ignore
        return get_balance, request_airdrop, None
    except Exception as e:
        return None, None, e

def _import_keypair():
    try:
        from backend.services.keypair_store import get_or_create_keypair  # type: ignore
        return get_or_create_keypair, None
    except Exception as e:
        return None, e

@router.get("/address")
def address():
    get_or_create_keypair, err = _import_keypair()
    if err is not None:
        raise HTTPException(status_code=500, detail=f"Keypair service unavailable: {err}")
    pub, prv = get_or_create_keypair()
    return {"public_key": pub}

@router.get("/balance")
def balance(address: Optional[str] = Query(None, description="Base58 Solana address (optional)")):
    get_balance, _, err = _import_solana_services()
    if err is not None:
        raise HTTPException(status_code=503, detail=f"Solana services unavailable: {err}")
    if address is None:
        get_or_create_keypair, kerr = _import_keypair()
        if kerr is not None:
            raise HTTPException(status_code=500, detail=f"Keypair service unavailable: {kerr}")
        address = get_or_create_keypair()[0]
    try:
        bal = get_balance(address)  # type: ignore[misc]
        return {"address": address, "balance_sol": bal, "ts": time.time()}
    except Exception as e:
        msg = str(e)
        if "Too Many Requests" in msg or "rate limit" in msg.lower():
            raise HTTPException(status_code=429, detail="RPC rate limit, please retry")
        raise HTTPException(status_code=500, detail=msg)

@router.post("/airdrop")
def airdrop(address: Optional[str] = None, sol: float = 0.2):
    _, request_airdrop, err = _import_solana_services()
    if err is not None:
        raise HTTPException(status_code=503, detail=f"Solana services unavailable: {err}")
    if address is None:
        get_or_create_keypair, kerr = _import_keypair()
        if kerr is not None:
            raise HTTPException(status_code=500, detail=f"Keypair service unavailable: {kerr}")
        address = get_or_create_keypair()[0]
    try:
        result = request_airdrop(address, sol)  # type: ignore[misc]
        return {"ok": True, **result}
    except Exception as e:
        msg = str(e)
        if "Too Many Requests" in msg or "rate limit" in msg.lower():
            raise HTTPException(status_code=429, detail="RPC rate limit, please retry")
        raise HTTPException(status_code=500, detail=msg)

@router.get("/health")
def wallet_health():
    _, _, err = _import_solana_services()
    if err is not None:
        return {"module":"wallet","solana_deps":f"missing ({err})","ts":time.time()}
    return {"module":"wallet","solana_deps":"ok","ts":time.time()}
