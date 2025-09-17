"""
Integration tests for the complete API workflow
"""
import pytest
import time
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestWalletIntegration:
    """Integration tests for wallet functionality"""

    def test_full_wallet_workflow(self, client, temp_keys_dir, monkeypatch):
        """Test complete wallet workflow from creation to balance check"""
        # Setup isolated keypair store
        from backend.services import keypair_store as ks
        monkeypatch.setattr(ks, "KEYS_DIR", temp_keys_dir, raising=False)
        monkeypatch.setattr(ks, "KEYFILE", temp_keys_dir / "solana_keypair.json", raising=False)

        # 1. Create/get wallet address
        r1 = client.get("/api/v1/wallet/address")
        assert r1.status_code == 200
        address = r1.json()["public_key"]
        assert address

        # 2. Check health
        r2 = client.get("/api/v1/wallet/health")
        assert r2.status_code == 200

        # 3. Mock balance check (would normally require Solana)
        import backend.api.wallet as wallet
        def fake_import_ok():
            def get_balance(addr):
                return 5.0 if addr == address else 0.0
            def request_airdrop(addr, sol):
                return {"signature": f"SIG_{sol}", "requested_sol": sol}
            return get_balance, request_airdrop, None
        monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)

        # 4. Check balance
        r3 = client.get("/api/v1/wallet/balance")
        assert r3.status_code == 200
        assert r3.json()["balance_sol"] == 5.0

        # 5. Test airdrop
        r4 = client.post("/api/v1/wallet/airdrop", json={"sol": 1.0})
        assert r4.status_code == 200
        assert "signature" in r4.json()


@pytest.mark.integration
class TestIdeasWorkflow:
    """Integration tests for ideas workflow"""

    def test_idea_lifecycle(self, client):
        """Test complete idea lifecycle"""
        # 1. Generate ideas
        r1 = client.post("/api/v1/agents/research/generate",
                        json={"time_value": 5, "time_unit": "minutes", "risk_pref": 3})
        assert r1.status_code == 200
        generation_result = r1.json()
        assert generation_result["count"] >= 1

        # 2. List ideas
        r2 = client.get("/api/v1/ideas/")
        assert r2.status_code == 200
        ideas = r2.json()
        assert isinstance(ideas, list)
        assert len(ideas) >= generation_result["count"]

        # 3. Get first idea details
        if ideas:
            idea_id = ideas[0]["id"]
            r3 = client.get(f"/api/v1/ideas/{idea_id}")
            assert r3.status_code == 200
            idea = r3.json()
            assert idea["id"] == idea_id

            # 4. Test idea state transitions
            transitions = [
                ("review", "NEEDS_REVIEW"),
                ("qa-ready", "READY_FOR_QA"),
                ("approve", "APPROVED"),
                ("schedule", "SCHEDULED")
            ]

            for action, expected_status in transitions:
                r = client.post(f"/api/v1/ideas/{idea_id}/{action}")
                if r.status_code == 200:
                    assert r.json()["status"] == expected_status
                elif r.status_code == 400:
                    # Some transitions might not be valid from current state
                    pass


@pytest.mark.integration
class TestTradesWorkflow:
    """Integration tests for trades workflow"""

    def test_trade_execution_workflow(self, client, temp_keys_dir, monkeypatch):
        """Test trade execution workflow"""
        # Setup wallet
        from backend.services import keypair_store as ks
        monkeypatch.setattr(ks, "KEYS_DIR", temp_keys_dir, raising=False)
        monkeypatch.setattr(ks, "KEYFILE", temp_keys_dir / "solana_keypair.json", raising=False)

        # Get wallet address
        r1 = client.get("/api/v1/wallet/address")
        assert r1.status_code == 200
        address = r1.json()["public_key"]

        # Mock trade execution
        import backend.api.trades as trades
        executed_trades = []

        def mock_execute_trade(action, address, amount, price=None):
            trade = {
                "id": f"trade_{len(executed_trades) + 1}",
                "action": action,
                "address": address,
                "quantity": amount,
                "price": price or 1.0,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            executed_trades.append(trade)
            return trade

        monkeypatch.setattr(trades, "execute_trade", mock_execute_trade)

        # Execute a trade
        r2 = client.post("/api/v1/trades/execute",
                        json={"action": "BUY", "address": address, "amount": 1.0, "price": 2.0})
        assert r2.status_code == 200
        trade = r2.json()
        assert trade["action"] == "BUY"
        assert trade["quantity"] == 1.0

        # Check trade history
        r3 = client.get("/api/v1/trades/recent")
        assert r3.status_code == 200
        recent_trades = r3.json()
        assert isinstance(recent_trades, list)


@pytest.mark.integration
@pytest.mark.slow
class TestSystemIntegration:
    """Slow integration tests for system-wide functionality"""

    def test_agents_status_integration(self, client):
        """Test that all agents are properly integrated"""
        r = client.get("/api/v1/agents/status")
        assert r.status_code == 200
        status = r.json()

        # Check all departments are present
        departments = ["research", "analysis", "quality", "execution"]
        for dept in departments:
            assert dept in status

    def test_full_system_health_check(self, client):
        """Test comprehensive system health"""
        endpoints = [
            "/api/v1/wallet/health",
            "/api/v1/agents/status",
            "/api/v1/strategies",
            "/api/v1/ideas/"
        ]

        for endpoint in endpoints:
            r = client.get(endpoint)
            assert r.status_code in [200, 404]  # 404 is acceptable for some endpoints

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import requests

        def make_request(endpoint):
            try:
                response = client.get(endpoint)
                return response.status_code
            except Exception as e:
                return str(e)

        endpoints = ["/api/v1/wallet/health"] * 5  # 5 concurrent requests

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, endpoints))

        # All should succeed
        for result in results:
            assert result == 200