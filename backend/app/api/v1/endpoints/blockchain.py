from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.db.mongodb import get_database
import logging
import hashlib
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

class TransactionType(str, Enum):
    MISSION_COMPLETION = "mission_completion"
    AGENT_STAKING = "agent_staking"
    REWARD_CLAIM = "reward_claim"
    DATA_STORAGE = "data_storage"
    NFT_MINT = "nft_mint"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

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
    confirmation_time: Optional[datetime] = None

class WalletBalance(BaseModel):
    wallet_address: str
    sol_balance: float
    nebula_balance: float
    last_updated: datetime

class TransactionRequest(BaseModel):
    transaction_type: TransactionType
    agent_id: Optional[str] = None
    mission_id: Optional[str] = None
    data_hash: Optional[str] = None
    amount: Optional[float] = None

class BlockchainRecordCreate(BaseModel):
    transaction_type: TransactionType
    agent_id: Optional[str] = None
    mission_id: Optional[str] = None
    data_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None
    arweave_hash: Optional[str] = None

# Helper function to convert ObjectId to string
def blockchain_helper(record) -> dict:
    if record:
        record["id"] = str(record["_id"])
        del record["_id"]
    return record

@router.get("/transactions", response_model=List[BlockchainRecord])
async def get_transactions(
    agent_id: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    limit: int = 100,
    skip: int = 0
):
    """Get blockchain transactions with optional filtering"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        # Build filter query
        filter_query = {}
        if agent_id:
            filter_query["agent_id"] = agent_id
        if transaction_type:
            filter_query["transaction_type"] = transaction_type.value
        if status:
            filter_query["status"] = status.value
        
        # Execute query with pagination
        cursor = blockchain_collection.find(filter_query).skip(skip).limit(limit).sort("timestamp", -1)
        transactions = []
        
        async for transaction in cursor:
            transactions.append(blockchain_helper(transaction))
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/record", response_model=BlockchainRecord)
async def record_mission_results(record_data: BlockchainRecordCreate):
    """Record mission results on Solana blockchain"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        # Generate transaction hash
        hash_input = f"{record_data.transaction_type}{record_data.agent_id}{record_data.mission_id}{datetime.now().isoformat()}"
        transaction_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Create blockchain record
        record_doc = {
            "transaction_hash": transaction_hash,
            "transaction_type": record_data.transaction_type.value,
            "status": TransactionStatus.PENDING.value,
            "agent_id": record_data.agent_id,
            "mission_id": record_data.mission_id,
            "data_hash": record_data.data_hash,
            "ipfs_hash": record_data.ipfs_hash,
            "arweave_hash": record_data.arweave_hash,
            "timestamp": datetime.now(),
            "block_number": None,
            "gas_used": None,
            "confirmation_time": None,
            "created_at": datetime.now()
        }
        
        # Insert record
        result = await blockchain_collection.insert_one(record_doc)
        record_doc["_id"] = result.inserted_id
        
        # TODO: Integrate with actual Solana blockchain
        # TODO: Store data on IPFS/Arweave
        # TODO: Record hash on Solana
        
        # Simulate transaction confirmation
        await asyncio.sleep(2)
        
        # Update record with confirmation
        await blockchain_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {
                "status": TransactionStatus.CONFIRMED.value,
                "block_number": 12345680 + result.inserted_id.generation_time,
                "gas_used": 30000,
                "confirmation_time": datetime.now()
            }}
        )
        
        # Get updated record
        updated_record = await blockchain_collection.find_one({"_id": result.inserted_id})
        
        logger.info(f"Recorded blockchain transaction {transaction_hash}")
        return blockchain_helper(updated_record)
        
    except Exception as e:
        logger.error(f"Error recording blockchain transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/transactions/{transaction_id}", response_model=BlockchainRecord)
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        transaction = await blockchain_collection.find_one({"_id": ObjectId(transaction_id)})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return blockchain_helper(transaction)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/transactions/hash/{transaction_hash}", response_model=BlockchainRecord)
async def get_transaction_by_hash(transaction_hash: str):
    """Get a transaction by blockchain hash"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        transaction = await blockchain_collection.find_one({"transaction_hash": transaction_hash})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return blockchain_helper(transaction)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching transaction by hash {transaction_hash}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/verify/{tx_id}")
async def verify_transaction(tx_id: str):
    """Verify a transaction on the blockchain"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        transaction = await blockchain_collection.find_one({"_id": ObjectId(tx_id)})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # TODO: Implement actual blockchain verification
        # For now, return mock verification data
        
        verification_result = {
            "transaction_id": tx_id,
            "transaction_hash": transaction["transaction_hash"],
            "verified": transaction["status"] == TransactionStatus.CONFIRMED.value,
            "block_number": transaction.get("block_number"),
            "confirmation_time": transaction.get("confirmation_time"),
            "gas_used": transaction.get("gas_used"),
            "ipfs_hash": transaction.get("ipfs_hash"),
            "arweave_hash": transaction.get("arweave_hash")
        }
        
        return verification_result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error verifying transaction {tx_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/balances", response_model=List[WalletBalance])
async def get_wallet_balances():
    """Get all wallet balances"""
    try:
        db = await get_database()
        balances_collection = db.wallet_balances
        
        cursor = balances_collection.find()
        balances = []
        
        async for balance in cursor:
            balances.append(blockchain_helper(balance))
        
        return balances
        
    except Exception as e:
        logger.error(f"Error fetching wallet balances: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/balances/{wallet_address}", response_model=WalletBalance)
async def get_wallet_balance(wallet_address: str):
    """Get balance for a specific wallet"""
    try:
        db = await get_database()
        balances_collection = db.wallet_balances
        
        balance = await balances_collection.find_one({"wallet_address": wallet_address})
        if not balance:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return blockchain_helper(balance)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching wallet balance {wallet_address}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/transactions", response_model=BlockchainRecord)
async def create_transaction(transaction_request: TransactionRequest):
    """Create a new blockchain transaction"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        # Generate transaction hash
        hash_input = f"{transaction_request.transaction_type}{transaction_request.agent_id}{transaction_request.mission_id}{datetime.now().isoformat()}"
        transaction_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Create transaction record
        transaction_doc = {
            "transaction_hash": transaction_hash,
            "transaction_type": transaction_request.transaction_type.value,
            "status": TransactionStatus.PENDING.value,
            "agent_id": transaction_request.agent_id,
            "mission_id": transaction_request.mission_id,
            "data_hash": transaction_request.data_hash,
            "ipfs_hash": None,
            "arweave_hash": None,
            "timestamp": datetime.now(),
            "block_number": None,
            "gas_used": None,
            "confirmation_time": None,
            "created_at": datetime.now()
        }
        
        # Insert transaction
        result = await blockchain_collection.insert_one(transaction_doc)
        transaction_doc["_id"] = result.inserted_id
        
        # TODO: Integrate with actual Solana blockchain
        # TODO: Add transaction retry logic and error handling
        
        # Simulate transaction confirmation
        await asyncio.sleep(2)
        
        # Update transaction with confirmation
        await blockchain_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {
                "status": TransactionStatus.CONFIRMED.value,
                "block_number": 12345680 + result.inserted_id.generation_time,
                "gas_used": 30000,
                "confirmation_time": datetime.now()
            }}
        )
        
        # Get updated transaction
        updated_transaction = await blockchain_collection.find_one({"_id": result.inserted_id})
        
        logger.info(f"Created blockchain transaction {transaction_hash}")
        return blockchain_helper(updated_transaction)
        
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agent/{agent_id}/transactions", response_model=List[BlockchainRecord])
async def get_agent_transactions(agent_id: str):
    """Get all transactions for a specific agent"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        cursor = blockchain_collection.find({"agent_id": agent_id}).sort("timestamp", -1)
        transactions = []
        
        async for transaction in cursor:
            transactions.append(blockchain_helper(transaction))
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error fetching agent transactions {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mission/{mission_id}/transactions", response_model=List[BlockchainRecord])
async def get_mission_transactions(mission_id: str):
    """Get all transactions for a specific mission"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        cursor = blockchain_collection.find({"mission_id": mission_id}).sort("timestamp", -1)
        transactions = []
        
        async for transaction in cursor:
            transactions.append(blockchain_helper(transaction))
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error fetching mission transactions {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_blockchain_stats():
    """Get blockchain statistics"""
    try:
        db = await get_database()
        blockchain_collection = db.blockchain_records
        
        # Get total counts
        total_transactions = await blockchain_collection.count_documents({})
        confirmed_transactions = await blockchain_collection.count_documents({"status": TransactionStatus.CONFIRMED.value})
        pending_transactions = await blockchain_collection.count_documents({"status": TransactionStatus.PENDING.value})
        failed_transactions = await blockchain_collection.count_documents({"status": TransactionStatus.FAILED.value})
        
        # Get transaction types distribution
        pipeline = [
            {"$group": {"_id": "$transaction_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        transaction_types = {}
        async for result in blockchain_collection.aggregate(pipeline):
            transaction_types[result["_id"]] = result["count"]
        
        # Get total gas used
        pipeline = [
            {"$group": {"_id": None, "total_gas": {"$sum": "$gas_used"}}}
        ]
        
        total_gas_result = await blockchain_collection.aggregate(pipeline).to_list(1)
        total_gas_used = total_gas_result[0]["total_gas"] if total_gas_result else 0
        
        return {
            "total_transactions": total_transactions,
            "confirmed_transactions": confirmed_transactions,
            "pending_transactions": pending_transactions,
            "failed_transactions": failed_transactions,
            "success_rate": confirmed_transactions / total_transactions if total_transactions > 0 else 0,
            "transaction_types": transaction_types,
            "total_gas_used": total_gas_used,
            "average_gas_per_transaction": total_gas_used / total_transactions if total_transactions > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching blockchain stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")