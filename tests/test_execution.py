from fastapi.testclient import TestClient

from src.main import app
from src.store import wallet_store, trades_store

client = TestClient(app)


def test_airdrop_execution():
    # ensure demo wallet exists
    addr = "So1anaEXAMPLEaddre55...............1234"
    wallet_store.clear()
    wallet_store[addr] = {"address": addr, "balance_sol": 1.0}
    trades_store.clear()

    payload = {"action": "AIRDROP", "address": addr, "amount": 0.5}
    r = client.post("/api/v1/trades/execute", json=payload)
    assert r.status_code == 200
    trade = r.json()
    assert trade["action"] == "AIRDROP"
    assert float(trade["quantity"]) == 0.5

    # wallet should be updated
    w = wallet_store.get(addr)
    assert w and w["balance_sol"] == 1.5
