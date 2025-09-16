# sepAI
Multi-agent research and execution software, with dashboard and company structure.

## Quick start (API)

Prerequisites: Python 3.10+

1) Install dependencies

```
pip install -r requirements.txt
```

2) Run the API (from `sepAI` root)

```
uvicorn src.main:app --reload
```

4) Run tests

```
# install deps and run pytest
./scripts/run_tests.ps1
```

3) Example endpoints

- `GET /api/v1/wallet/balance` â€” demo wallet balance
- `POST /api/v1/ideas` â€” create an idea (JSON body)
- `GET /api/v1/trades/recent` â€” recent trades (demo data)
- `GET /api/v1/agents/status` â€” agent versions/status
- `GET /api/v1/strategies` â€” list strategies
- `GET /api/v1/releases` â€” list releases

## Dashboard (mock)

Open `docs/ceo_dashboard_mock_v16.html` in a browser. Initial buttons are wired to API (balance, idea-create) for a basic end-to-end demo.






## Configuration

Environment variables:

- ALLOW_ORIGINS — comma-separated allowed origins for CORS (default *). Example: http://localhost:5173,http://127.0.0.1:5173
- REDIS_URL — optional Redis connection (e.g., 
edis://localhost:6379/0). If unset or unavailable, an in-memory fallback is used.

See .env.example for a starter.

