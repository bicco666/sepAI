import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.state import validate_budget

def test_budget_policy():
    """Test budget policy validation"""
    # Test valid budgets
    assert validate_budget(0.01, "solana") == True
    assert validate_budget(0.001, "ethereum") == True
    assert validate_budget(0.04, "solana") == True  # At the limit

    # Test invalid budgets (too high)
    assert validate_budget(0.1, "solana") == False
    assert validate_budget(1.0, "ethereum") == False
    assert validate_budget(0.05, "solana") == False  # Over the limit

    print("✅ Budget policy test passed")

if __name__ == "__main__":
    test_budget_policy()