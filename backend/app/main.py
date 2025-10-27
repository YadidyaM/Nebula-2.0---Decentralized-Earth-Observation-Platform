from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.services.blockchain.solana_client import SolanaClient
from app.agents.orchestrator import OrchestratorAgent
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator
from app.services.satellite_physics import satellite_physics_engine

# Global variables for services
solana_client = None
orchestrator = None
swarms_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Nebula Protocol Backend...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    print("✅ Connected to MongoDB")
    
    # Initialize Solana client
    global solana_client
    solana_client = SolanaClient()
    await solana_client.initialize()
    print("✅ Solana client initialized")
    
    # Initialize Swarms AI orchestrator
    global swarms_orchestrator
    swarms_orchestrator = SwarmsOrchestrator()
    await swarms_orchestrator.initialize()
    print("✅ Swarms AI orchestrator initialized")
    
    # Initialize agent orchestrator
    global orchestrator
    orchestrator = OrchestratorAgent(solana_client, swarms_orchestrator)
    await orchestrator.start()
    print("✅ Agent orchestrator started")
    
    # Initialize satellite physics engine
    await satellite_physics_engine.initialize()
    print("✅ Satellite physics engine initialized")
    
    print("🌟 Nebula Protocol Backend ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Nebula Protocol Backend...")
    if orchestrator:
        await orchestrator.stop()
    await satellite_physics_engine.shutdown()
    await close_mongo_connection()
    print("✅ Shutdown complete")

app = FastAPI(
    title="Nebula Protocol API",
    description="Decentralized Earth observation platform with AI agents and blockchain",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Nebula Protocol API",
        "version": "1.0.0",
        "status": "operational",
        "agents": "9 specialized AI agents active",
        "blockchain": "Solana integration active",
        "storage": "IPFS/Arweave decentralized storage"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mongodb": "connected",
        "solana": "connected" if solana_client else "disconnected",
        "swarms_ai": "connected" if swarms_orchestrator else "disconnected",
        "orchestrator": "active" if orchestrator else "inactive",
        "satellite_physics": "active" if satellite_physics_engine.is_running else "inactive"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
