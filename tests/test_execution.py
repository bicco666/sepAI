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


def test_buy_and_sell_execution():
    addr = "So1anaEXAMPLEaddre55...............1234"
    wallet_store.clear()
    wallet_store[addr] = {"address": addr, "balance_sol": 10.0}
    trades_store.clear()

    # BUY 0.5 SOL at price 2.0 -> cost 1.0
    payload = {"action": "BUY", "address": addr, "amount": 0.5, "price": 2.0}
    r = client.post("/api/v1/trades/execute", json=payload)
    assert r.status_code == 200
    trade = r.json()
    assert trade["action"] == "BUY"
    assert float(trade["quantity"]) == 0.5
    # wallet debited
    w = wallet_store.get(addr)
    assert w and w["balance_sol"] == 9.0

    # SELL 0.2 SOL at price 3.0 -> proceeds 0.6
    payload = {"action": "SELL", "address": addr, "amount": 0.2, "price": 3.0}
    r = client.post("/api/v1/trades/execute", json=payload)
    assert r.status_code == 200
    trade = r.json()
    assert trade["action"] == "SELL"
    w = wallet_store.get(addr)
    assert w and abs(w["balance_sol"] - 9.6) < 1e-9
