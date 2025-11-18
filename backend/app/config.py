from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Swarms AI
    swarms_ai_api_key: str = os.getenv("SWARMS_AI_API_KEY", "")
    
    # Gemini AI
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    gemini_vision_model: str = os.getenv("GEMINI_VISION_MODEL", "gemini-pro-vision")
    gemini_flash_model: str = os.getenv("GEMINI_FLASH_MODEL", "gemini-flash")
    
    # Solana
    solana_rpc_url: str = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
    solana_network: str = os.getenv("SOLANA_NETWORK", "devnet")
    mission_registry_program: str = os.getenv("MISSION_REGISTRY_PROGRAM", "")
    staking_program: str = os.getenv("STAKING_PROGRAM", "")
    nebula_token_mint: str = os.getenv("NEBULA_TOKEN_MINT", "")
    
    # Agent Wallets
    orchestrator_wallet_private_key: str = os.getenv("ORCHESTRATOR_WALLET_PRIVATE_KEY", "")
    forest_guardian_wallet_private_key: str = os.getenv("FOREST_GUARDIAN_WALLET_PRIVATE_KEY", "")
    ice_sentinel_wallet_private_key: str = os.getenv("ICE_SENTINEL_WALLET_PRIVATE_KEY", "")
    storm_tracker_wallet_private_key: str = os.getenv("STORM_TRACKER_WALLET_PRIVATE_KEY", "")
    urban_monitor_wallet_private_key: str = os.getenv("URBAN_MONITOR_WALLET_PRIVATE_KEY", "")
    water_watcher_wallet_private_key: str = os.getenv("WATER_WATCHER_WALLET_PRIVATE_KEY", "")
    security_sentinel_wallet_private_key: str = os.getenv("SECURITY_SENTINEL_WALLET_PRIVATE_KEY", "")
    land_surveyor_wallet_private_key: str = os.getenv("LAND_SURVEYOR_WALLET_PRIVATE_KEY", "")
    disaster_responder_wallet_private_key: str = os.getenv("DISASTER_RESPONDER_WALLET_PRIVATE_KEY", "")
    
    # IPFS/Arweave
    pinata_api_key: str = os.getenv("PINATA_API_KEY", "")
    pinata_secret_key: str = os.getenv("PINATA_SECRET_KEY", "")
    arweave_wallet_key: str = os.getenv("ARWEAVE_WALLET_KEY", "")
    bundlr_node_url: str = os.getenv("BUNDLR_NODE_URL", "https://node1.bundlr.network")
    
    # Environmental Data APIs
    nasa_api_key: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
    esa_copernicus_username: str = os.getenv("ESA_COPERNICUS_USERNAME", "")
    esa_copernicus_password: str = os.getenv("ESA_COPERNICUS_PASSWORD", "")
    noaa_api_token: str = os.getenv("NOAA_API_TOKEN", "")
    sentinel_hub_client_id: str = os.getenv("SENTINEL_HUB_CLIENT_ID", "")
    sentinel_hub_client_secret: str = os.getenv("SENTINEL_HUB_CLIENT_SECRET", "")
    usgs_api_key: str = os.getenv("USGS_API_KEY", "")
    
    # Database
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/nebula")
    
    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key")
    
    # WebSocket
    ws_port: int = int(os.getenv("WS_PORT", "8001"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
