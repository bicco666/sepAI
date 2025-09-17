import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

def test_dashboard():
    """Test dashboard API endpoints"""
    with app.test_client() as client:
        # Test health endpoint
        resp = client.get('/healthz')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "status" in data
        assert "timestamp" in data

        # Test ideas endpoint
        resp = client.get('/api/v1/ideas')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "ideas" in data

        # Test orders endpoint
        resp = client.get('/api/v1/orders')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "orders" in data

        # Test test endpoint
        resp = client.get('/api/v1/tests/run?case=1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "success" in data

        print("✅ Dashboard test passed")

if __name__ == "__main__":
    test_dashboard()