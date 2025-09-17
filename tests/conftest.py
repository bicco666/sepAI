"""
Shared pytest fixtures and configuration for all tests
"""
import pytest
import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import importlib


@pytest.fixture(scope="session")
def app():
    """Application fixture for the entire test session"""
    m = importlib.import_module("backend.main")
    return getattr(m, "app")


@pytest.fixture
def client(app):
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Temporary directory fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_keys_dir(temp_dir):
    """Temporary keys directory fixture"""
    keys_dir = temp_dir / "keys"
    keys_dir.mkdir(exist_ok=True)
    return keys_dir


@pytest.fixture
def mock_solana_services():
    """Mock Solana services for testing"""
    def get_balance(addr):
        return 1.0

    def request_airdrop(addr, sol):
        return {"signature": f"SIG_{sol}", "requested_sol": sol}

    return get_balance, request_airdrop, None


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables after each test"""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def isolated_keypair_store(temp_keys_dir, monkeypatch):
    """Isolated keypair store for testing"""
    from backend.services import keypair_store as ks
    monkeypatch.setattr(ks, "KEYS_DIR", temp_keys_dir, raising=False)
    monkeypatch.setattr(ks, "KEYFILE", temp_keys_dir / "solana_keypair.json", raising=False)
    return ks


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "api: mark test as API test")