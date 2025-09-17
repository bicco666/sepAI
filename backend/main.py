import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.services import ideas, analysis as strategies, execution as trades, wallet, reporting as tests, audit
from backend.api import agents

app = FastAPI(title="Solana Trading Organisation API", version="0.1")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers FIRST (before static files)
app.include_router(wallet.router, prefix="/api/v1/wallet")
app.include_router(agents.router, prefix="/api/v1/agents")
app.include_router(ideas.router, prefix="/api/v1/ideas")
app.include_router(strategies.router, prefix="/api/v1/strategies")
app.include_router(trades.router, prefix="/api/v1/trades")
app.include_router(tests.router, prefix="/api/v1/tests")
app.include_router(audit.router, prefix="/api/v1/audit")

# Add a simple health check
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Mount static files LAST (fallback for everything else)
app.mount("/", StaticFiles(directory=".", html=True), name="static")