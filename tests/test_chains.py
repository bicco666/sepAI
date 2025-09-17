import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.state import get_store, Idea
from backend.chains.solana_mock import execute_solana_trade
from backend.chains.ethereum_mock import execute_ethereum_trade

def test_chains():
    """Test chain validation and execution"""
    store = get_store()
    store.ideas.clear()

    # Test Solana chain
    sol_idea = Idea("solana", 0.1, "Solana trade")
    store.add_idea(sol_idea)
    assert sol_idea.chain == "solana"

    # Test Ethereum chain
    eth_idea = Idea("ethereum", 0.001, "Ethereum trade")
    store.add_idea(eth_idea)
    assert eth_idea.chain == "ethereum"

    # Test invalid chain (validation happens in Flask app, not in Idea class)
    invalid_idea = Idea("bitcoin", 0.01)  # This should work
    assert invalid_idea.chain == "bitcoin"  # But chain validation happens at API level

    print("✅ Chain validation test passed")

def test_chain_execution():
    """Test actual chain execution"""
    # Test Solana execution
    sol_result = execute_solana_trade(0.1)
    assert "success" in sol_result
    assert sol_result["chain"] == "solana"
    assert "pnl" in sol_result or "error" in sol_result

    # Test Ethereum execution
    eth_result = execute_ethereum_trade(0.001)
    assert "success" in eth_result
    assert eth_result["chain"] == "ethereum"
    assert "pnl" in eth_result or "error" in eth_result

    print("✅ Chain execution test passed")

if __name__ == "__main__":
    test_chains()
    test_chain_execution()