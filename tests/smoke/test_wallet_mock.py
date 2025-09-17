import requests
def test_wallet_balance_mock():
    r = requests.get("http://localhost:8000/api/v1/wallet/balance")
    assert r.status_code==200 and isinstance(r.json().get("balance"), (int,float))