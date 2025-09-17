import os
import json
from pathlib import Path
from fastapi.testclient import TestClient
import importlib
import time

# Wir erwarten, dass das Projekt im gleichen Verzeichnis liegt, eine Ebene höher o. via PYTHONPATH=. gestartet wird.
# Falls nicht, PYTHONPATH entsprechend setzen.

# Hilfsfunktion: App importieren
def get_app():
    m = importlib.import_module("backend.main")
    return getattr(m, "app")

def client():
    return TestClient(get_app())

# --- Test 1: /wallet/address erzeugt/liest Keypair (ohne Solana-Abhängigkeiten notwendig) ---
def test_wallet_address_creates_file(tmp_path, monkeypatch):
    # isoliertes keys-Verzeichnis
    keys_dir = tmp_path / "keys"
    monkeypatch.setattr("backend.services.keypair_store.KEYS_DIR", keys_dir, raising=False)
    monkeypatch.setattr("backend.services.keypair_store.KEYFILE", keys_dir / "solana_keypair.json", raising=False)
    c = client()
    r = c.get("/api/v1/wallet/address")
    assert r.status_code == 200
    data = r.json()
    assert "public_key" in data and isinstance(data["public_key"], str) and len(data["public_key"]) >= 20
    assert (keys_dir / "solana_keypair.json").exists()

# --- Test 2: /wallet/health liefert 200 und Status-Info ---
def test_wallet_health_ok():
    c = client()
    r = c.get("/api/v1/wallet/health")
    assert r.status_code == 200
    assert "module" in r.json()

# --- Test 3: /wallet/balance ohne Solana-Deps -> 503 ---
def test_wallet_balance_without_solana(monkeypatch):
    # Force _import_solana_services to return error
    import backend.api.wallet as wallet
    def fake_import():
        return None, None, Exception("No solana installed")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import)
    c = client()
    r = c.get("/api/v1/wallet/balance")
    assert r.status_code == 503
    assert "unavailable" in r.json()["detail"].lower()

# --- Test 4: /wallet/balance mit Mock get_balance -> 200 ---
def test_wallet_balance_with_mock(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    def fake_import_ok():
        def get_balance(addr): return 1.2345
        def request_airdrop(addr, sol): return {"signature":"SIG", "requested_sol":sol}
        return get_balance, request_airdrop, None
    # Keypair Pfade mocken, damit address-Default funktioniert
    keys_dir = tmp_path / "keys"
    monkeypatch.setattr("backend.services.keypair_store.KEYS_DIR", keys_dir, raising=False)
    monkeypatch.setattr("backend.services.keypair_store.KEYFILE", keys_dir / "solana_keypair.json", raising=False)
    # Erst Adresse erzeugen
    c = client()
    c.get("/api/v1/wallet/address")
    # Jetzt Solana-Services mocken
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    r = c.get("/api/v1/wallet/balance")
    assert r.status_code == 200
    assert abs(r.json()["balance_sol"] - 1.2345) < 1e-9

# --- Test 5: /wallet/airdrop mit Mock -> 200 & signature ---
def test_wallet_airdrop_with_mock(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    def fake_import_ok():
        def get_balance(addr): return 0.0
        def request_airdrop(addr, sol): return {"signature":"S1GNEr", "requested_sol":sol}
        return get_balance, request_airdrop, None
    keys_dir = tmp_path / "keys"
    monkeypatch.setattr("backend.services.keypair_store.KEYS_DIR", keys_dir, raising=False)
    monkeypatch.setattr("backend.services.keypair_store.KEYFILE", keys_dir / "solana_keypair.json", raising=False)
    c = client()
    c.get("/api/v1/wallet/address")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    r = c.post("/api/v1/wallet/airdrop", data={"sol":0.2})
    assert r.status_code == 200
    assert "signature" in r.json()

# --- Test 6: /wallet/airdrop mit RateLimit -> 429 ---
def test_wallet_airdrop_rate_limited(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    def fake_import_ok():
        def get_balance(addr): return 0.0
        def request_airdrop(addr, sol): raise RuntimeError("Too Many Requests")
        return get_balance, request_airdrop, None
    keys_dir = tmp_path / "keys"
    monkeypatch.setattr("backend.services.keypair_store.KEYS_DIR", keys_dir, raising=False)
    monkeypatch.setattr("backend.services.keypair_store.KEYFILE", keys_dir / "solana_keypair.json", raising=False)
    c = client()
    c.get("/api/v1/wallet/address")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    r = c.post("/api/v1/wallet/airdrop", data={"sol":0.2})
    assert r.status_code == 429

# --- Test 7: /wallet/balance invalid address -> 500 (aktuelle Implementierung validiert nicht explizit) ---
def test_wallet_balance_invalid_address(monkeypatch):
    import backend.api.wallet as wallet
    def fake_import_ok():
        def get_balance(addr): raise RuntimeError("Invalid address")
        def request_airdrop(addr, sol): return {"signature":"sig", "requested_sol":sol}
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    c = client()
    r = c.get("/api/v1/wallet/balance?address=BAD")
    assert r.status_code == 500
    assert "invalid" in r.json()["detail"].lower()

# --- Test 8: /agents/research/generate erzeugt Ideen ---
def test_agents_research_generate_creates_ideas():
    c = client()
    r = c.post("/api/v1/agents/research/generate", json={"time_value": 10, "time_unit":"minutes", "risk_pref": 3})
    assert r.status_code == 200
    data = r.json()
    assert "count" in data and data["count"] >= 1
    # Liste prüfen
    r2 = c.get("/api/v1/ideas/")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
    assert len(r2.json()) >= data["count"]

# --- Test 9: /agents/status liefert alle vier Departments ---
def test_agents_status_minimal():
    c = client()
    r = c.get("/api/v1/agents/status")
    assert r.status_code == 200
    js = r.json()
    for k in ["research","analysis","quality","execution"]:
        assert k in js

# --- Test 10: /wallet/address zweimal -> gleicher Key ---
def test_wallet_address_persistence(tmp_path, monkeypatch):
    keys_dir = tmp_path / "keys"
    monkeypatch.setattr("backend.services.keypair_store.KEYS_DIR", keys_dir, raising=False)
    monkeypatch.setattr("backend.services.keypair_store.KEYFILE", keys_dir / "solana_keypair.json", raising=False)
    c = client()
    r1 = c.get("/api/v1/wallet/address").json()["public_key"]
    r2 = c.get("/api/v1/wallet/address").json()["public_key"]
    assert r1 == r2
    assert (keys_dir / "solana_keypair.json").exists()
