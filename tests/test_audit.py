import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import run_full_audit

def test_audit():
    """Test audit functionality"""
    audit_results = run_full_audit()

    # Check that audit returns expected structure
    assert "timestamp" in audit_results
    assert "ideas_count" in audit_results
    assert "orders_count" in audit_results
    assert "budget_total" in audit_results
    assert "ideas_by_state" in audit_results
    assert "orders_by_state" in audit_results

    # Check that counts are reasonable
    assert isinstance(audit_results["ideas_count"], int)
    assert isinstance(audit_results["orders_count"], int)
    assert audit_results["budget_total"] > 0

    print("✅ Audit test passed")
    print(f"Audit results: {audit_results}")

if __name__ == "__main__":
    test_audit()