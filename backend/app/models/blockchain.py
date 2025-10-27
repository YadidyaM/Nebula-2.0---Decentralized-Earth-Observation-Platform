from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    MISSION_COMPLETION = "mission_completion"
    AGENT_STAKING = "agent_staking"
    REWARD_CLAIM = "reward_claim"
    DATA_STORAGE = "data_storage"
    NFT_MINT = "nft_mint"
    TOKEN_TRANSFER = "token_transfer"
    SMART_CONTRACT_CALL = "smart_contract_call"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BlockchainRecord(BaseModel):
    id: str
    transaction_hash: str
    transaction_type: TransactionType
    status: TransactionStatus
    agent_id: Optional[str] = None
    mission_id: Optional[str] = None
    data_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None
    arweave_hash: Optional[str] = None
    timestamp: datetime
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    gas_price: Optional[int] = None
    confirmation_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class WalletBalance(BaseModel):
    wallet_address: str
    sol_balance: float
    nebula_balance: float
    last_updated: datetime
    transaction_count: int = 0
    total_gas_used: int = 0

class SmartContractCall(BaseModel):
    contract_address: str
    function_name: str
    parameters: Dict[str, Any]
    agent_id: str
    mission_id: Optional[str] = None
    timestamp: datetime
    transaction_hash: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING
    gas_estimate: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class NFTMetadata(BaseModel):
    token_id: str
    agent_id: str
    name: str
    description: str
    image_url: str
    attributes: List[Dict[str, Any]]
    rarity: str
    minted_at: datetime
    owner: str
    staked: bool = False
    staked_at: Optional[datetime] = None
    rewards_earned: float = 0.0
