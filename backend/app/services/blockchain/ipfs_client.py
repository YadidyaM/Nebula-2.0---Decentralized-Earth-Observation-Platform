import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.config import settings

logger = logging.getLogger(__name__)

class IPFSClient:
    """IPFS client for decentralized storage via Pinata"""
    
    def __init__(self):
        self.api_key = settings.pinata_api_key
        self.secret_key = settings.pinata_secret_key
        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
            "Content-Type": "application/json"
        }
    
    async def upload_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Upload data to IPFS via Pinata"""
        try:
            # Prepare the data for upload
            upload_data = {
                "pinataContent": data,
                "pinataMetadata": {
                    "name": f"nebula_data_{datetime.now().isoformat()}",
                    "keyvalues": metadata or {}
                }
            }
            
            # Upload to Pinata
            response = requests.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=self.headers,
                json=upload_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result["IpfsHash"]
                logger.info(f"Data uploaded to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"IPFS upload failed: {response.text}")
                raise Exception(f"IPFS upload failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to upload to IPFS: {e}")
            raise e
    
    async def upload_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Upload a file to IPFS via Pinata"""
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                
                pinata_metadata = {
                    "name": f"nebula_file_{datetime.now().isoformat()}",
                    "keyvalues": metadata or {}
                }
                
                response = requests.post(
                    f"{self.base_url}/pinning/pinFileToIPFS",
                    headers={
                        "pinata_api_key": self.api_key,
                        "pinata_secret_api_key": self.secret_key
                    },
                    files=files,
                    data={"pinataMetadata": json.dumps(pinata_metadata)},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ipfs_hash = result["IpfsHash"]
                    logger.info(f"File uploaded to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    logger.error(f"IPFS file upload failed: {response.text}")
                    raise Exception(f"IPFS file upload failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to upload file to IPFS: {e}")
            raise e
    
    async def retrieve_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """Retrieve data from IPFS"""
        try:
            # Use public IPFS gateway
            response = requests.get(f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Data retrieved from IPFS: {ipfs_hash}")
                return data
            else:
                logger.error(f"Failed to retrieve from IPFS: {response.text}")
                raise Exception(f"Failed to retrieve from IPFS: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to retrieve from IPFS: {e}")
            raise e
    
    async def pin_hash(self, ipfs_hash: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Pin an existing IPFS hash to Pinata"""
        try:
            pin_data = {
                "hashToPin": ipfs_hash,
                "pinataMetadata": {
                    "name": f"nebula_pin_{datetime.now().isoformat()}",
                    "keyvalues": metadata or {}
                }
            }
            
            response = requests.post(
                f"{self.base_url}/pinning/pinByHash",
                headers=self.headers,
                json=pin_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Hash pinned to Pinata: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to pin hash: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pin hash: {e}")
            return False
    
    async def get_pin_list(self) -> List[Dict[str, Any]]:
        """Get list of pinned content"""
        try:
            response = requests.get(
                f"{self.base_url}/data/pinList",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("rows", [])
            else:
                logger.error(f"Failed to get pin list: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get pin list: {e}")
            return []
    
    async def unpin_hash(self, ipfs_hash: str) -> bool:
        """Unpin a hash from Pinata"""
        try:
            response = requests.delete(
                f"{self.base_url}/pinning/unpin/{ipfs_hash}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Hash unpinned from Pinata: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to unpin hash: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to unpin hash: {e}")
            return False
