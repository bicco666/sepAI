import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import wallet, agents, ideas

app = FastAPI(title="Solana Trading Organisation API", version="0.1")

# CORS for frontend
origins_env = "*"  # Simplified for testing
allow_origins = [origins_env]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers FIRST (before static files)
app.include_router(wallet.router, prefix="/api/v1/wallet")
app.include_router(agents.router, prefix="/api/v1/agents")
app.include_router(ideas.router, prefix="/api/v1/ideas")

# Add a simple health check
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Mount static files LAST (fallback for everything else)
app.mount("/", StaticFiles(directory=".", html=True), name="static")