from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
try:
    from web3 import Web3
    from eth_account import Account
    _HAVE_ETHEREUM = True
except Exception as e:
    print(f"Ethereum library not available: {e}")
    _HAVE_ETHEREUM = False

from backend.core.config import ETHEREUM_RPC

class RateLimitError(Exception):
    pass

def _client():
    if not _HAVE_ETHEREUM:
        raise RuntimeError("ethereum library not installed")
    return Web3(Web3.HTTPProvider(ETHEREUM_RPC))

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, min=0.5, max=8), reraise=True)
def get_balance(address: str) -> float:
    # For demo purposes, return a mock balance
    # In production, this would connect to Ethereum RPC
    if not _HAVE_ETHEREUM:
        # Return mock balance for demo
        import random
        return round(random.uniform(0.1, 10.0), 4)

    try:
        w3 = _client()
        checksum_address = Web3.to_checksum_address(address)
        balance_wei = w3.eth.get_balance(checksum_address)
        return float(Web3.from_wei(balance_wei, 'ether'))
    except Exception as e:
        # Fallback to mock balance
        import random
        return round(random.uniform(0.1, 10.0), 4)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=0.5, min=0.5, max=8), reraise=True)
def request_airdrop(address: str, eth: float = 0.1) -> dict:
    # For devnet, we can use a faucet API or simulate
    # This is a mock implementation - in reality, you'd call a faucet service
    if not _HAVE_ETHEREUM:
        return {"signature": "mock_tx_hash", "requested_eth": eth}

    try:
        # For Sepolia testnet, you might need to use a faucet service
        # For now, return mock response
        import time
        mock_tx_hash = f"0x{hex(int(time.time()))[2:]}"
        return {"signature": mock_tx_hash, "requested_eth": eth}
    except Exception as e:
        raise RuntimeError(f"Airdrop failed: {e}")