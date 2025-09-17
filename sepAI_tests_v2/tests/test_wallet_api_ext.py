import os, sys, json, importlib, types, time
from pathlib import Path
from fastapi.testclient import TestClient

def get_app():
    m = importlib.import_module("backend.main")
    return getattr(m, "app")

def client():
    return TestClient(get_app())

# --- Group A: Service availability / graceful degradation ---

def test_balance_returns_503_when_solana_missing(monkeypatch):
    import backend.api.wallet as wallet
    def fake_import():
        return None, None, Exception("solana library not installed")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import)
    c = client()
    r = c.get("/api/v1/wallet/balance")
    assert r.status_code == 503
    assert "solana" in r.json()["detail"].lower()

def test_airdrop_returns_503_when_solana_missing(monkeypatch):
    import backend.api.wallet as wallet
    def fake_import():
        return None, None, Exception("solana.publickey not found")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import)
    c = client()
    r = c.post("/api/v1/wallet/airdrop", data={"sol":0.2})
    assert r.status_code == 503
    assert "solana" in r.json()["detail"].lower()

def test_health_shows_missing_when_solana_missing(monkeypatch):
    import backend.api.wallet as wallet
    def fake_import():
        return None, None, Exception("solana not installed")
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import)
    c = client()
    r = c.get("/api/v1/wallet/health")
    assert r.status_code == 200
    js = r.json()
    assert js["module"] == "wallet"
    assert "missing" in js["solana_deps"]

# --- Group B: Happy path via mocks ---

def test_balance_ok_with_mock(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    # make sure default address exists
    from backend.services import keypair_store
    monkeypatch.setattr(keypair_store, "KEYS_DIR", tmp_path/"keys", raising=False)
    monkeypatch.setattr(keypair_store, "KEYFILE", tmp_path/"keys"/"solana_keypair.json", raising=False)
    # ensure address created
    from backend.services.keypair_store import get_or_create_keypair
    pub, prv = get_or_create_keypair()
    def fake_import_ok():
        def get_balance(addr): assert addr==pub; return 0.7777
        def request_airdrop(addr, sol): return {"signature":"SIGOK","requested_sol":sol}
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    c = client()
    r = c.get("/api/v1/wallet/balance")
    assert r.status_code == 200
    assert abs(r.json()["balance_sol"] - 0.7777) < 1e-9

def test_airdrop_ok_with_mock_form_and_json(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    from backend.services import keypair_store
    monkeypatch.setattr(keypair_store, "KEYS_DIR", tmp_path/"keys", raising=False)
    monkeypatch.setattr(keypair_store, "KEYFILE", tmp_path/"keys"/"solana_keypair.json", raising=False)
    from backend.services.keypair_store import get_or_create_keypair
    pub, prv = get_or_create_keypair()
    calls = {"count":0,"last_sol":None}
    def fake_import_ok():
        def get_balance(addr): return 0.0
        def request_airdrop(addr, sol):
            calls["count"]+=1; calls["last_sol"]=sol
            return {"signature":"SIGFORMJSON","requested_sol":sol}
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    c = client()
    # form-encoded
    r1 = c.post("/api/v1/wallet/airdrop", data={"sol":0.2})
    # json body (optional path)
    r2 = c.post("/api/v1/wallet/airdrop", json={"sol":0.3})
    assert r1.status_code==200 and r2.status_code==200
    assert calls["count"]==2
    assert abs(calls["last_sol"]-0.3)<1e-9

# --- Group C: Error mapping accuracy ---

def test_airdrop_rate_limit_maps_429(monkeypatch, tmp_path):
    import backend.api.wallet as wallet
    from backend.services import keypair_store
    monkeypatch.setattr(keypair_store, "KEYS_DIR", tmp_path/"keys", raising=False)
    monkeypatch.setattr(keypair_store, "KEYFILE", tmp_path/"keys"/"solana_keypair.json", raising=False)
    from backend.services.keypair_store import get_or_create_keypair
    get_or_create_keypair()
    def fake_import_ok():
        def get_balance(addr): return 0.0
        def request_airdrop(addr, sol): raise RuntimeError("Too Many Requests")
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    c = client()
    r = c.post("/api/v1/wallet/airdrop", data={"sol":0.2})
    assert r.status_code == 429

def test_balance_internal_error_maps_500(monkeypatch):
    import backend.api.wallet as wallet
    def fake_import_ok():
        def get_balance(addr): raise RuntimeError("RPC exploded")
        def request_airdrop(addr, sol): return {"signature":"X","requested_sol":sol}
        return get_balance, request_airdrop, None
    monkeypatch.setattr(wallet, "_import_solana_services", fake_import_ok)
    c = client()
    r = c.get("/api/v1/wallet/balance?address=ANY")
    assert r.status_code == 500
    assert "rpc" in r.json()["detail"].lower()

# --- Group D: Config & RPC environment ---

def test_uses_env_solana_rpc(monkeypatch):
    # Verify that backend.core.config.SOLANA_RPC reads env
    import backend.core.config as cfg
    monkeypatch.setenv("SOLANA_RPC", "https://example.devnet/")
    importlib.reload(cfg)
    assert cfg.SOLANA_RPC.startswith("https://example.devnet/")

# --- Group E: Address creation & persistence ---

def test_address_endpoint_creates_and_persists(tmp_path, monkeypatch):
    from backend.services import keypair_store
    monkeypatch.setattr(keypair_store, "KEYS_DIR", tmp_path/"keys", raising=False)
    monkeypatch.setattr(keypair_store, "KEYFILE", tmp_path/"keys"/"solana_keypair.json", raising=False)
    c = client()
    a1 = c.get("/api/v1/wallet/address").json()["public_key"]
    a2 = c.get("/api/v1/wallet/address").json()["public_key"]
    assert a1 == a2
    assert (tmp_path/"keys"/"solana_keypair.json").exists()

# --- Group F: Ideas/Agents integration sanity ---

def test_agents_generate_creates_ideas_and_list_has_items():
    c = client()
    r = c.post("/api/v1/agents/research/generate", json={"time_value": 5, "time_unit":"minutes", "risk_pref": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    r2 = c.get("/api/v1/ideas/")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list) and len(r2.json()) >= data["count"]
