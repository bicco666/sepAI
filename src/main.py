import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import wallet, ideas, strategies, trades, agents, releases

app = FastAPI(title="Solana Trading Organisation API", version="0.1")

# CORS for frontend
origins_env = os.getenv("ALLOW_ORIGINS", "*")
allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Configure via ALLOW_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wallet.router, prefix="/api/v1")
app.include_router(ideas.router, prefix="/api/v1")
app.include_router(strategies.router, prefix="/api/v1")
app.include_router(trades.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(releases.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Solana Trading Organisation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
