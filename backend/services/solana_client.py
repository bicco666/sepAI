from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
try:
    from solana.rpc.api import Client
    from solana.publickey import PublicKey
    _HAVE_SOLANA = True
except Exception:
    _HAVE_SOLANA = False

from backend.core.config import SOLANA_RPC

class RateLimitError(Exception):
    pass

def _client():
    if not _HAVE_SOLANA:
        raise RuntimeError("solana library not installed")
    return Client(SOLANA_RPC, timeout=30)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, min=0.5, max=8), reraise=True)
def get_balance(address: str) -> float:
    c = _client()
    resp = c.get_balance(PublicKey(address))
    if resp.get("error"):
        err = str(resp["error"])
        if "Too Many Requests" in err:
            raise RateLimitError(err)
        raise RuntimeError(err)
    lamports = resp["result"]["value"]
    return lamports / 1_000_000_000

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, min=0.5, max=8), reraise=True)
def request_airdrop(address: str, sol: float = 0.2) -> dict:
    c = _client()
    lamports = int(sol * 1_000_000_000)
    resp = c.request_airdrop(PublicKey(address), lamports)
    if resp.get("error"):
        err = str(resp["error"])
        if "Too Many Requests" in err:
            raise RateLimitError(err)
        raise RuntimeError(err)
    sig = resp["result"]
    return {"signature": sig, "requested_sol": sol}
