"""
Performance tests for API endpoints
"""
import pytest
import time
import statistics
from fastapi.testclient import TestClient


@pytest.mark.slow
class TestPerformance:
    """Performance tests for API endpoints"""

    def test_wallet_address_response_time(self, client, benchmark):
        """Test wallet address endpoint response time"""
        def get_address():
            return client.get("/api/v1/wallet/address")

        result = benchmark(get_address)
        assert result.status_code == 200
        # Should respond within 100ms
        assert result.stats.mean < 0.1

    def test_wallet_health_response_time(self, client):
        """Test wallet health endpoint response time"""
        start_time = time.time()
        r = client.get("/api/v1/wallet/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert r.status_code == 200
        assert response_time < 0.05  # Should respond within 50ms

    def test_concurrent_wallet_balance_requests(self, client, temp_keys_dir, monkeypatch):
        """Test concurrent balance requests"""
        # Setup
        from backend.services import keypair_store as ks
        monkeypatch.setattr(ks, "KEYS_DIR", temp_keys_dir, raising=False)
        monkeypatch.setattr(ks, "KEYFILE", temp_keys_dir / "solana_keypair.json", raising=False)

        import backend.api.wallet as wallet
        def fake_import_ok():
            def get_balance(addr): return 1.0
            def request_airdrop(addr, sol): return {"signature": "SIG", "requested_sol": sol}
            return get_balance, request_airdrop, None
        monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)

        # Test concurrent requests
        import concurrent.futures
        response_times = []

        def make_balance_request():
            start = time.time()
            r = client.get("/api/v1/wallet/balance")
            end = time.time()
            response_times.append(end - start)
            return r.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: make_balance_request(), range(10)))

        # All should succeed
        assert all(status == 200 for status in results)

        # Check performance
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 0.2  # Average under 200ms
        assert max_response_time < 0.5  # Max under 500ms

    def test_memory_usage_growth(self, client):
        """Test for memory leaks in repeated requests"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make many requests
        for i in range(100):
            client.get("/api/v1/wallet/health")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal (< 10MB)
        assert memory_growth < 10

    def test_database_connection_pooling(self, client):
        """Test database connection efficiency"""
        # This would test Redis connection pooling if implemented
        # For now, just test basic connectivity
        start_time = time.time()

        for i in range(50):
            r = client.get("/api/v1/agents/status")
            assert r.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 50

        # Should handle 50 requests efficiently
        assert avg_time < 0.1  # Under 100ms per request
        assert total_time < 2.0  # Under 2 seconds total


@pytest.mark.slow
class TestLoadTests:
    """Load testing for high-volume scenarios"""

    def test_high_frequency_requests(self, client):
        """Test handling of high-frequency requests"""
        import threading
        import queue

        results = queue.Queue()
        errors = []

        def worker():
            try:
                for i in range(20):  # 20 requests per worker
                    start = time.time()
                    r = client.get("/api/v1/wallet/health")
                    end = time.time()

                    results.put({
                        'status': r.status_code,
                        'response_time': end - start
                    })
            except Exception as e:
                errors.append(str(e))

        # Start 5 workers
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"

        response_times = []
        while not results.empty():
            result = results.get()
            assert result['status'] == 200
            response_times.append(result['response_time'])

        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile

        assert avg_response_time < 0.1  # Average under 100ms
        assert p95_response_time < 0.2  # 95th percentile under 200ms

    def test_large_payload_handling(self, client):
        """Test handling of large request payloads"""
        # Test with large idea generation request
        large_request = {
            "time_value": 1000,
            "time_unit": "minutes",
            "risk_pref": 5,
            "additional_data": "x" * 10000  # 10KB of data
        }

        start_time = time.time()
        r = client.post("/api/v1/agents/research/generate", json=large_request)
        end_time = time.time()

        response_time = end_time - start_time

        # Should handle large payload reasonably well
        assert r.status_code in [200, 422]  # 422 for validation error is acceptable
        assert response_time < 1.0  # Under 1 second