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
 - API_KEY — optional API key to protect sensitive endpoints (e.g. `/api/v1/trades/execute`). If unset, auth is disabled for local dev.
 - SOLANA_RPC_URL — optional Solana RPC URL (e.g. devnet RPC). If set, the Execution adapter will attempt to perform real RPC calls when `live=true` is passed to execute endpoints.
 - ALLOW_MAINNET_TRANSACTIONS — set to a truthy value (`1`, `true`, `yes`) to allow mainnet transactions. Default: disabled. Use with caution.
 - ENABLE_INTERNET_RESEARCH — set to a truthy value to allow the research agent to fetch token lists from public APIs (e.g. CoinGecko). Default: disabled (safer for offline/dev).

See .env.example for a starter.

