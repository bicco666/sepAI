from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include routers
app.include_router(wallet.router, prefix="/api/v1/wallet")
app.include_router(agents.router, prefix="/api/v1/agents")
app.include_router(ideas.router, prefix="/api/v1/ideas")