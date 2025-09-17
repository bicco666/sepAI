import requests
def test_health_and_list():
    assert requests.get("http://localhost:8000/healthz").status_code==200
    assert requests.get("http://localhost:8000/api/v1/ideas").status_code==200