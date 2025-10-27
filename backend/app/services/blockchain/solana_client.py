from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from typing import Dict, List, Optional, Any
import json
import logging
import os
from cryptography.fernet import Fernet
import base64

from app.config import settings

logger = logging.getLogger(__name__)

class SolanaClient:
    """Solana blockchain client for agent transactions"""
    
    def __init__(self):
        self.client = Client(settings.solana_rpc_url)
        self.network = settings.solana_network
        self.agent_wallets: Dict[str, Keypair] = {}
        self.encryption_key = settings.encryption_key.encode()
        self.fernet = Fernet(self.encryption_key)
        
    async def initialize(self):
        """Initialize Solana client and load agent wallets"""
        try:
            # Test connection
            version = self.client.get_version()
            logger.info(f"Connected to Solana {self.network}: {version}")
            
            # Load agent wallets
            await self._load_agent_wallets()
            
        except Exception as e:
            logger.error(f"Failed to initialize Solana client: {e}")
            raise e
    
    async def _load_agent_wallets(self):
        """Load and decrypt agent wallet keypairs"""
        wallet_keys = {
            "orchestrator": settings.orchestrator_wallet_private_key,
            "forest_guardian": settings.forest_guardian_wallet_private_key,
            "ice_sentinel": settings.ice_sentinel_wallet_private_key,
            "storm_tracker": settings.storm_tracker_wallet_private_key,
            "urban_monitor": settings.urban_monitor_wallet_private_key,
            "water_watcher": settings.water_watcher_wallet_private_key,
            "security_sentinel": settings.security_sentinel_wallet_private_key,
            "land_surveyor": settings.land_surveyor_wallet_private_key,
            "disaster_responder": settings.disaster_responder_wallet_private_key,
        }
        
        for agent_name, encrypted_key in wallet_keys.items():
            if encrypted_key:
                try:
                    # Decrypt the private key
                    decrypted_key = self.fernet.decrypt(encrypted_key.encode())
                    keypair = Keypair.from_secret_key(decrypted_key)
                    self.agent_wallets[agent_name] = keypair
                    logger.info(f"Loaded wallet for {agent_name}: {keypair.public_key}")
                except Exception as e:
                    logger.error(f"Failed to load wallet for {agent_name}: {e}")
                    # Generate new wallet if loading fails
                    keypair = Keypair()
                    self.agent_wallets[agent_name] = keypair
                    logger.info(f"Generated new wallet for {agent_name}: {keypair.public_key}")
    
    def get_agent_wallet(self, agent_name: str) -> Optional[Keypair]:
        """Get wallet keypair for an agent"""
        return self.agent_wallets.get(agent_name)
    
    async def get_balance(self, public_key: str) -> float:
        """Get SOL balance for a public key"""
        try:
            pubkey = PublicKey(public_key)
            balance = self.client.get_balance(pubkey)
            return balance.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Failed to get balance for {public_key}: {e}")
            return 0.0
    
    async def send_transaction(self, from_agent: str, to_address: str, amount: float) -> str:
        """Send SOL from agent wallet to another address"""
        try:
            from_keypair = self.get_agent_wallet(from_agent)
            if not from_keypair:
                raise ValueError(f"No wallet found for agent {from_agent}")
            
            to_pubkey = PublicKey(to_address)
            lamports = int(amount * 1e9)  # Convert SOL to lamports
            
            # Create transfer transaction
            transaction = Transaction().add(
                transfer(
                    TransferParams(
                        from_pubkey=from_keypair.public_key,
                        to_pubkey=to_pubkey,
                        lamports=lamports,
                    )
                )
            )
            
            # Send transaction
            result = self.client.send_transaction(transaction, from_keypair)
            transaction_hash = result.value
            
            logger.info(f"Transaction sent: {transaction_hash}")
            return str(transaction_hash)
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise e
    
    async def record_mission_completion(self, agent_name: str, mission_id: str, data_hash: str) -> str:
        """Record mission completion on blockchain"""
        try:
            agent_wallet = self.get_agent_wallet(agent_name)
            if not agent_wallet:
                raise ValueError(f"No wallet found for agent {agent_name}")
            
            # Create mission completion transaction
            # This would interact with the mission registry smart contract
            # For now, we'll create a simple transaction
            
            transaction_data = {
                "type": "mission_completion",
                "agent": agent_name,
                "mission_id": mission_id,
                "data_hash": data_hash,
                "timestamp": str(int(time.time()))
            }
            
            # In a real implementation, this would call the smart contract
            # For now, we'll simulate the transaction
            transaction_hash = f"mission_{mission_id}_{int(time.time())}"
            
            logger.info(f"Mission completion recorded: {transaction_hash}")
            return transaction_hash
            
        except Exception as e:
            logger.error(f"Failed to record mission completion: {e}")
            raise e
    
    async def stake_agent_nft(self, agent_name: str, nft_mint: str) -> str:
        """Stake agent NFT for rewards"""
        try:
            agent_wallet = self.get_agent_wallet(agent_name)
            if not agent_wallet:
                raise ValueError(f"No wallet found for agent {agent_name}")
            
            # Create staking transaction
            # This would interact with the staking smart contract
            transaction_data = {
                "type": "nft_staking",
                "agent": agent_name,
                "nft_mint": nft_mint,
                "timestamp": str(int(time.time()))
            }
            
            # Simulate staking transaction
            transaction_hash = f"stake_{nft_mint}_{int(time.time())}"
            
            logger.info(f"Agent NFT staked: {transaction_hash}")
            return transaction_hash
            
        except Exception as e:
            logger.error(f"Failed to stake agent NFT: {e}")
            raise e
    
    async def claim_rewards(self, agent_name: str) -> str:
        """Claim staking rewards for an agent"""
        try:
            agent_wallet = self.get_agent_wallet(agent_name)
            if not agent_wallet:
                raise ValueError(f"No wallet found for agent {agent_name}")
            
            # Create reward claim transaction
            transaction_data = {
                "type": "reward_claim",
                "agent": agent_name,
                "timestamp": str(int(time.time()))
            }
            
            # Simulate reward claim transaction
            transaction_hash = f"claim_{agent_name}_{int(time.time())}"
            
            logger.info(f"Rewards claimed: {transaction_hash}")
            return transaction_hash
            
        except Exception as e:
            logger.error(f"Failed to claim rewards: {e}")
            raise e
    
    def generate_wallet(self, agent_name: str) -> Dict[str, str]:
        """Generate a new wallet for an agent"""
        keypair = Keypair()
        
        # Encrypt the private key
        private_key_bytes = bytes(keypair.secret_key)
        encrypted_key = self.fernet.encrypt(private_key_bytes)
        
        return {
            "public_key": str(keypair.public_key),
            "private_key": encrypted_key.decode(),
            "agent_name": agent_name
        }
    
    async def get_transaction_status(self, transaction_hash: str) -> Dict[str, Any]:
        """Get status of a transaction"""
        try:
            # In a real implementation, this would query the blockchain
            # For now, we'll simulate the response
            return {
                "transaction_hash": transaction_hash,
                "status": "confirmed",
                "block_number": 12345678,
                "gas_used": 50000,
                "timestamp": str(int(time.time()))
            }
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return {"error": str(e)}
