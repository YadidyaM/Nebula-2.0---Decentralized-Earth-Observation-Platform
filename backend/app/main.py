# Main FastAPI application entry point with LangGraph orchestrator, Gemini AI, and enhanced satellite physics initialization
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.services.blockchain.solana_client import SolanaClient
from app.agents.specialized.orchestrator import Orchestrator
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator
from app.services.ai.gemini_service import gemini_service
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
    
    # Initialize Gemini AI service
    if gemini_service.is_available():
        print("✅ Gemini AI service initialized")
    else:
        print("⚠️  Gemini AI service not available (API key may be missing)")
    
    # Initialize agent orchestrator with LangGraph workflows
    global orchestrator
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    print("✅ Agent orchestrator with LangGraph workflows initialized")
    
    # Initialize enhanced satellite physics engine with Poliastro, Skyfield
    await satellite_physics_engine.initialize()
    print("✅ Enhanced satellite physics engine initialized")
    
    print("🌟 Nebula Protocol Backend ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Nebula Protocol Backend...")
    if orchestrator:
        orchestrator.running = False
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
        "gemini_ai": "available" if gemini_service.is_available() else "unavailable",
        "langgraph": "active" if orchestrator and orchestrator.langgraph_orchestrator else "inactive",
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
