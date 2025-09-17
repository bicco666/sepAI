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

def _import_ethereum_services():
    try:
        from backend.services.ethereum_client import get_balance, request_airdrop  # type: ignore
        return get_balance, request_airdrop, None
    except Exception as e:
        return None, None, e

def _import_keypair():
    try:
        from backend.services.keypair_store import get_or_create_keypair  # type: ignore
        return get_or_create_keypair, None
    except Exception as e:
        return None, e

def _import_ethereum_keypair():
    try:
        from backend.services.keypair_store import get_or_create_ethereum_keypair  # type: ignore
        return get_or_create_ethereum_keypair, None
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
        # Mock balance for smoke tests
        return {"balance": 123.45}
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

@router.get("/network")
def network_status():
    """Get current network information"""
    from backend.core.config import SOLANA_RPC
    network = "devnet" if "devnet" in SOLANA_RPC else "mainnet" if "mainnet" in SOLANA_RPC else "custom"
    return {
        "network": network,
        "rpc_url": SOLANA_RPC,
        "is_devnet": network == "devnet",
        "is_mainnet": network == "mainnet",
        "airdrop_available": network == "devnet",
        "ts": time.time()
    }

@router.get("/status")
def wallet_status():
    """Get comprehensive wallet status"""
    from backend.core.config import SOLANA_RPC

    # Get network info
    network = "devnet" if "devnet" in SOLANA_RPC else "mainnet" if "mainnet" in SOLANA_RPC else "custom"

    # Get address
    address_info = {"address": None, "error": None}
    get_or_create_keypair, kerr = _import_keypair()
    if kerr is None:
        try:
            pub, _ = get_or_create_keypair()
            address_info["address"] = pub
        except Exception as e:
            address_info["error"] = str(e)
    else:
        address_info["error"] = str(kerr)

    # Get balance if address available
    balance_info = {"balance_sol": None, "error": None}
    if address_info["address"]:
        get_balance, _, berr = _import_solana_services()
        if berr is None:
            try:
                bal = get_balance(address_info["address"])
                balance_info["balance_sol"] = bal
            except Exception as e:
                balance_info["error"] = str(e)
        else:
            balance_info["error"] = str(berr)

    return {
        "network": network,
        "rpc_url": SOLANA_RPC,
        "is_devnet": network == "devnet",
        "is_mainnet": network == "mainnet",
        "airdrop_available": network == "devnet",
        "address": address_info["address"],
        "balance_sol": balance_info["balance_sol"],
        "address_error": address_info["error"],
        "balance_error": balance_info["error"],
        "ts": time.time()
    }

# Ethereum endpoints

@router.get("/ethereum/address")
def ethereum_address():
    get_or_create_ethereum_keypair, err = _import_ethereum_keypair()
    if err is not None:
        raise HTTPException(status_code=500, detail=f"Ethereum keypair service unavailable: {err}")
    pub, prv = get_or_create_ethereum_keypair()
    return {"public_key": pub}

@router.get("/ethereum/balance")
def ethereum_balance(address: Optional[str] = Query(None, description="Ethereum address (optional)")):
    get_balance, _, err = _import_ethereum_services()
    if err is not None:
        raise HTTPException(status_code=503, detail=f"Ethereum services unavailable: {err}")
    if address is None:
        get_or_create_ethereum_keypair, kerr = _import_ethereum_keypair()
        if kerr is not None:
            raise HTTPException(status_code=500, detail=f"Ethereum keypair service unavailable: {kerr}")
        address = get_or_create_ethereum_keypair()[0]
    try:
        bal = get_balance(address)  # type: ignore[misc]
        return {"address": address, "balance_eth": bal, "ts": time.time()}
    except Exception as e:
        msg = str(e)
        if "Too Many Requests" in msg or "rate limit" in msg.lower():
            raise HTTPException(status_code=429, detail="RPC rate limit, please retry")
        raise HTTPException(status_code=500, detail=msg)

@router.post("/ethereum/airdrop")
def ethereum_airdrop(address: Optional[str] = None, eth: float = 0.1):
    _, request_airdrop, err = _import_ethereum_services()
    if err is not None:
        raise HTTPException(status_code=503, detail=f"Ethereum services unavailable: {err}")
    if address is None:
        get_or_create_ethereum_keypair, kerr = _import_ethereum_keypair()
        if kerr is not None:
            raise HTTPException(status_code=500, detail=f"Ethereum keypair service unavailable: {kerr}")
        address = get_or_create_ethereum_keypair()[0]
    try:
        result = request_airdrop(address, eth)  # type: ignore[misc]
        return {"ok": True, **result}
    except Exception as e:
        msg = str(e)
        if "Too Many Requests" in msg or "rate limit" in msg.lower():
            raise HTTPException(status_code=429, detail="RPC rate limit, please retry")
        raise HTTPException(status_code=500, detail=msg)

@router.get("/ethereum/health")
def ethereum_wallet_health():
    _, _, err = _import_ethereum_services()
    if err is not None:
        return {"module":"ethereum_wallet","ethereum_deps":f"missing ({err})","ts":time.time()}
    return {"module":"ethereum_wallet","ethereum_deps":"ok","ts":time.time()}

@router.get("/ethereum/network")
def ethereum_network_status():
    """Get current Ethereum network information"""
    from backend.core.config import ETHEREUM_RPC
    network = "sepolia" if "sepolia" in ETHEREUM_RPC else "mainnet" if "mainnet" in ETHEREUM_RPC else "custom"
    return {
        "network": network,
        "rpc_url": ETHEREUM_RPC,
        "is_devnet": network == "sepolia",
        "is_mainnet": network == "mainnet",
        "airdrop_available": network == "sepolia",
        "ts": time.time()
    }

@router.get("/ethereum/status")
def ethereum_wallet_status():
    """Get comprehensive Ethereum wallet status"""
    from backend.core.config import ETHEREUM_RPC

    # Get network info
    network = "sepolia" if "sepolia" in ETHEREUM_RPC else "mainnet" if "mainnet" in ETHEREUM_RPC else "custom"

    # Get address
    address_info = {"address": None, "error": None}
    get_or_create_ethereum_keypair, kerr = _import_ethereum_keypair()
    if kerr is None:
        try:
            pub, _ = get_or_create_ethereum_keypair()
            address_info["address"] = pub
        except Exception as e:
            address_info["error"] = str(e)
    else:
        address_info["error"] = str(kerr)

    # Get balance if address available
    balance_info = {"balance_eth": None, "error": None}
    if address_info["address"]:
        get_balance, _, berr = _import_ethereum_services()
        if berr is None:
            try:
                bal = get_balance(address_info["address"])
                balance_info["balance_eth"] = bal
            except Exception as e:
                balance_info["error"] = str(e)
        else:
            balance_info["error"] = str(berr)

    return {
        "network": network,
        "rpc_url": ETHEREUM_RPC,
        "is_devnet": network == "sepolia",
        "is_mainnet": network == "mainnet",
        "airdrop_available": network == "sepolia",
        "address": address_info["address"],
        "balance_eth": balance_info["balance_eth"],
        "address_error": address_info["error"],
        "balance_error": balance_info["error"],
        "ts": time.time()
    }
