import time
import random

def execute_solana_trade(amount: float) -> dict:
    """
    Mock execution for Solana trades
    Returns success/failure with simulated delay
    """
    time.sleep(0.1)  # Simulate network delay

    # Simulate 80% success rate
    success = random.random() < 0.8

    if success:
        # Simulate some profit/loss
        pnl = amount * (random.uniform(-0.1, 0.2))
        return {
            "success": True,
            "chain": "solana",
            "amount": amount,
            "pnl": round(pnl, 4),
            "tx_hash": f"sol_{random.randint(100000, 999999)}",
            "executed_at": time.time()
        }
    else:
        return {
            "success": False,
            "chain": "solana",
            "amount": amount,
            "error": "Transaction failed",
            "executed_at": time.time()
        }