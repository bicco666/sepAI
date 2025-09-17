import requests
def test_flow_basic():
    r = requests.post("http://localhost:8000/api/v1/ideas/generate", json={"risk":3,"asset":"SOL"})
    assert r.status_code in (200,201); idea = r.json()
    a = requests.post(f"http://localhost:8000/api/v1/ideas/{idea['id']}/analyze")
    assert a.status_code==200
    o = requests.post(f"http://localhost:8000/api/v1/ideas/{idea['id']}/to_orders")
    assert o.status_code in (200,201)