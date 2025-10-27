import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.config import settings

logger = logging.getLogger(__name__)

class ArweaveClient:
    """Arweave client for permanent decentralized storage via Bundlr"""
    
    def __init__(self):
        self.wallet_key = settings.arweave_wallet_key
        self.bundlr_node_url = settings.bundlr_node_url
        self.base_url = f"{self.bundlr_node_url}"
    
    async def upload_data(self, data: Dict[str, Any], tags: Optional[List[Dict[str, str]]] = None) -> str:
        """Upload data to Arweave for permanent storage"""
        try:
            # Prepare the transaction data
            transaction_data = {
                "data": json.dumps(data),
                "tags": tags or [
                    {"name": "Content-Type", "value": "application/json"},
                    {"name": "App-Name", "value": "Nebula-Protocol"},
                    {"name": "Timestamp", "value": str(int(datetime.now().timestamp()))}
                ]
            }
            
            # Upload to Bundlr
            response = requests.post(
                f"{self.base_url}/tx",
                json=transaction_data,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                arweave_id = result["id"]
                logger.info(f"Data uploaded to Arweave: {arweave_id}")
                return arweave_id
            else:
                logger.error(f"Arweave upload failed: {response.text}")
                raise Exception(f"Arweave upload failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to upload to Arweave: {e}")
            raise e
    
    async def upload_file(self, file_path: str, tags: Optional[List[Dict[str, str]]] = None) -> str:
        """Upload a file to Arweave for permanent storage"""
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                
                # Prepare transaction
                transaction_data = {
                    "data": file_data.decode('utf-8') if isinstance(file_data, bytes) else file_data,
                    "tags": tags or [
                        {"name": "Content-Type", "value": "application/octet-stream"},
                        {"name": "App-Name", "value": "Nebula-Protocol"},
                        {"name": "Timestamp", "value": str(int(datetime.now().timestamp()))}
                    ]
                }
                
                response = requests.post(
                    f"{self.base_url}/tx",
                    json=transaction_data,
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    arweave_id = result["id"]
                    logger.info(f"File uploaded to Arweave: {arweave_id}")
                    return arweave_id
                else:
                    logger.error(f"Arweave file upload failed: {response.text}")
                    raise Exception(f"Arweave file upload failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to upload file to Arweave: {e}")
            raise e
    
    async def retrieve_data(self, arweave_id: str) -> Dict[str, Any]:
        """Retrieve data from Arweave"""
        try:
            # Use Arweave gateway
            response = requests.get(f"https://arweave.net/{arweave_id}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Data retrieved from Arweave: {arweave_id}")
                return data
            else:
                logger.error(f"Failed to retrieve from Arweave: {response.text}")
                raise Exception(f"Failed to retrieve from Arweave: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to retrieve from Arweave: {e}")
            raise e
    
    async def get_transaction_info(self, arweave_id: str) -> Dict[str, Any]:
        """Get transaction information from Arweave"""
        try:
            response = requests.get(f"https://arweave.net/tx/{arweave_id}", timeout=30)
            
            if response.status_code == 200:
                info = response.json()
                logger.info(f"Transaction info retrieved: {arweave_id}")
                return info
            else:
                logger.error(f"Failed to get transaction info: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get transaction info: {e}")
            return {}
    
    async def search_transactions(self, tags: List[Dict[str, str]], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for transactions by tags"""
        try:
            # Build query
            query_parts = []
            for tag in tags:
                query_parts.append(f"{tag['name']}:{tag['value']}")
            
            query = " AND ".join(query_parts)
            
            response = requests.get(
                f"https://arweave.net/query?query={query}&limit={limit}",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                transactions = result.get("data", {}).get("transactions", {}).get("edges", [])
                logger.info(f"Found {len(transactions)} transactions")
                return transactions
            else:
                logger.error(f"Failed to search transactions: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to search transactions: {e}")
            return []
    
    async def get_wallet_balance(self) -> float:
        """Get wallet balance in AR tokens"""
        try:
            if not self.wallet_key:
                logger.warning("No wallet key configured")
                return 0.0
            
            # This would require wallet integration
            # For now, return a mock balance
            logger.info("Wallet balance retrieved")
            return 1.5  # Mock balance
            
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            return 0.0
    
    async def estimate_cost(self, data_size: int) -> Dict[str, Any]:
        """Estimate the cost of uploading data"""
        try:
            # Get current price from Bundlr
            response = requests.get(f"{self.base_url}/price/{data_size}", timeout=30)
            
            if response.status_code == 200:
                price_info = response.json()
                return {
                    "data_size": data_size,
                    "price_ar": price_info.get("price", 0),
                    "price_usd": price_info.get("price_usd", 0),
                    "currency": "AR"
                }
            else:
                logger.error(f"Failed to estimate cost: {response.text}")
                return {"error": "Failed to estimate cost"}
                
        except Exception as e:
            logger.error(f"Failed to estimate cost: {e}")
            return {"error": str(e)}
