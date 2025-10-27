from fastapi import APIRouter
from app.api.v1.endpoints import missions, agents, telemetry, blockchain, websocket, satellite_physics

api_router = APIRouter()

api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(satellite_physics.router, prefix="/satellites", tags=["satellite-physics"])
