"""
Tests for blockchain integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.services.blockchain.solana_client import SolanaClient
from app.models.blockchain import TransactionType, TransactionStatus

@pytest.mark.blockchain
class TestSolanaClient:
    """Test cases for Solana client functionality."""
    
    @pytest.fixture
    async def solana_client(self):
        """Create a Solana client instance."""
        client = SolanaClient()
        await client.initialize()
        return client
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, solana_client):
        """Test Solana client initialization."""
        assert solana_client is not None
        assert hasattr(solana_client, 'is_connected')
        assert hasattr(solana_client, 'rpc_url')
    
    @pytest.mark.asyncio
    async def test_connection_status(self, solana_client):
        """Test connection status checking."""
        # Mock the connection check
        with patch.object(solana_client, '_check_connection') as mock_check:
            mock_check.return_value = True
            is_connected = await solana_client.check_connection()
            assert is_connected is True
    
    @pytest.mark.asyncio
    async def test_get_balance(self, solana_client):
        """Test getting wallet balance."""
        # Mock the balance retrieval
        with patch.object(solana_client, '_get_balance') as mock_balance:
            mock_balance.return_value = 1000000000  # 1 SOL in lamports
            balance = await solana_client.get_balance("test_wallet_address")
            assert balance == 1000000000
    
    @pytest.mark.asyncio
    async def test_send_transaction(self, solana_client):
        """Test sending transactions."""
        # Mock transaction sending
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.return_value = "test_transaction_hash"
            
            transaction_data = {
                "to": "recipient_wallet",
                "amount": 1000000000,  # 1 SOL in lamports
                "memo": "Test transaction"
            }
            
            tx_hash = await solana_client.send_transaction(transaction_data)
            assert tx_hash == "test_transaction_hash"
    
    @pytest.mark.asyncio
    async def test_create_mission_transaction(self, solana_client):
        """Test creating mission transactions."""
        mission_data = {
            "mission_id": "test_mission_123",
            "agent_id": "test_agent_456",
            "reward_amount": 1000,
            "mission_type": "environmental_monitoring"
        }
        
        with patch.object(solana_client, '_create_mission_transaction') as mock_create:
            mock_create.return_value = "mission_tx_hash"
            
            tx_hash = await solana_client.create_mission_transaction(mission_data)
            assert tx_hash == "mission_tx_hash"
    
    @pytest.mark.asyncio
    async def test_stake_agent(self, solana_client):
        """Test staking agent functionality."""
        stake_data = {
            "agent_id": "test_agent_123",
            "amount": 5000000000,  # 5 SOL in lamports
            "duration": 30  # 30 days
        }
        
        with patch.object(solana_client, '_stake_agent') as mock_stake:
            mock_stake.return_value = "stake_tx_hash"
            
            tx_hash = await solana_client.stake_agent(stake_data)
            assert tx_hash == "stake_tx_hash"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status(self, solana_client):
        """Test getting transaction status."""
        tx_hash = "test_transaction_hash"
        
        with patch.object(solana_client, '_get_transaction_status') as mock_status:
            mock_status.return_value = {
                "status": "confirmed",
                "slot": 12345,
                "confirmation_time": "2024-01-01T00:00:00Z"
            }
            
            status = await solana_client.get_transaction_status(tx_hash)
            assert status["status"] == "confirmed"
            assert status["slot"] == 12345
    
    @pytest.mark.asyncio
    async def test_error_handling(self, solana_client):
        """Test error handling in Solana client."""
        # Test connection error
        with patch.object(solana_client, '_check_connection') as mock_check:
            mock_check.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                await solana_client.check_connection()
        
        # Test transaction error
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.side_effect = Exception("Transaction failed")
            
            with pytest.raises(Exception):
                await solana_client.send_transaction({})

@pytest.mark.blockchain
class TestBlockchainModels:
    """Test cases for blockchain data models."""
    
    def test_transaction_type_enum(self):
        """Test TransactionType enum."""
        from app.models.blockchain import TransactionType
        
        assert TransactionType.MISSION_COMPLETION == "mission_completion"
        assert TransactionType.AGENT_STAKING == "agent_staking"
        assert TransactionType.REWARD_DISTRIBUTION == "reward_distribution"
        assert TransactionType.PENALTY == "penalty"
    
    def test_transaction_status_enum(self):
        """Test TransactionStatus enum."""
        from app.models.blockchain import TransactionStatus
        
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.CONFIRMED == "confirmed"
        assert TransactionStatus.FAILED == "failed"
        assert TransactionStatus.CANCELLED == "cancelled"
    
    def test_blockchain_record_creation(self):
        """Test BlockchainRecord model creation."""
        from app.models.blockchain import BlockchainRecord, BlockchainRecordCreate
        
        record_data = BlockchainRecordCreate(
            transaction_hash="test_hash_123",
            transaction_type=TransactionType.MISSION_COMPLETION,
            agent_id="test_agent_456",
            mission_id="test_mission_789",
            amount=1000,
            status=TransactionStatus.CONFIRMED,
            block_number=12345,
            gas_used=21000
        )
        
        assert record_data.transaction_hash == "test_hash_123"
        assert record_data.transaction_type == TransactionType.MISSION_COMPLETION
        assert record_data.agent_id == "test_agent_456"
        assert record_data.amount == 1000
        assert record_data.status == TransactionStatus.CONFIRMED

@pytest.mark.blockchain
class TestBlockchainIntegration:
    """Integration tests for blockchain functionality."""
    
    @pytest.mark.asyncio
    async def test_mission_lifecycle_blockchain(self):
        """Test mission lifecycle with blockchain integration."""
        solana_client = SolanaClient()
        
        # Mock the entire blockchain interaction
        with patch.object(solana_client, 'create_mission_transaction') as mock_create:
            with patch.object(solana_client, 'get_transaction_status') as mock_status:
                with patch.object(solana_client, 'send_transaction') as mock_send:
                    
                    # Setup mocks
                    mock_create.return_value = "mission_tx_hash"
                    mock_status.return_value = {"status": "confirmed"}
                    mock_send.return_value = "reward_tx_hash"
                    
                    # Test mission creation
                    mission_data = {
                        "mission_id": "test_mission",
                        "agent_id": "test_agent",
                        "reward_amount": 1000
                    }
                    
                    tx_hash = await solana_client.create_mission_transaction(mission_data)
                    assert tx_hash == "mission_tx_hash"
                    
                    # Test transaction confirmation
                    status = await solana_client.get_transaction_status(tx_hash)
                    assert status["status"] == "confirmed"
    
    @pytest.mark.asyncio
    async def test_agent_staking_workflow(self):
        """Test agent staking workflow."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, 'stake_agent') as mock_stake:
            with patch.object(solana_client, 'get_transaction_status') as mock_status:
                
                # Setup mocks
                mock_stake.return_value = "stake_tx_hash"
                mock_status.return_value = {"status": "confirmed"}
                
                # Test staking
                stake_data = {
                    "agent_id": "test_agent",
                    "amount": 5000000000,  # 5 SOL
                    "duration": 30
                }
                
                tx_hash = await solana_client.stake_agent(stake_data)
                assert tx_hash == "stake_tx_hash"
                
                # Test confirmation
                status = await solana_client.get_transaction_status(tx_hash)
                assert status["status"] == "confirmed"
    
    @pytest.mark.asyncio
    async def test_reward_distribution_system(self):
        """Test reward distribution system."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, 'distribute_rewards') as mock_distribute:
            with patch.object(solana_client, 'get_transaction_status') as mock_status:
                
                # Setup mocks
                mock_distribute.return_value = "reward_tx_hash"
                mock_status.return_value = {"status": "confirmed"}
                
                # Test reward distribution
                reward_data = {
                    "agent_id": "test_agent",
                    "amount": 1000,
                    "mission_id": "test_mission",
                    "reason": "mission_completion"
                }
                
                tx_hash = await solana_client.distribute_rewards(reward_data)
                assert tx_hash == "reward_tx_hash"
                
                # Test confirmation
                status = await solana_client.get_transaction_status(tx_hash)
                assert status["status"] == "confirmed"

@pytest.mark.blockchain
class TestBlockchainErrorHandling:
    """Test cases for blockchain error handling."""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, '_check_connection') as mock_check:
            mock_check.side_effect = Exception("Network timeout")
            
            with pytest.raises(Exception, match="Network timeout"):
                await solana_client.check_connection()
    
    @pytest.mark.asyncio
    async def test_transaction_failure_handling(self):
        """Test handling of transaction failures."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.side_effect = Exception("Insufficient funds")
            
            with pytest.raises(Exception, match="Insufficient funds"):
                await solana_client.send_transaction({})
    
    @pytest.mark.asyncio
    async def test_invalid_transaction_handling(self):
        """Test handling of invalid transactions."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.side_effect = Exception("Invalid transaction format")
            
            with pytest.raises(Exception, match="Invalid transaction format"):
                await solana_client.send_transaction({"invalid": "data"})

@pytest.mark.blockchain
class TestBlockchainPerformance:
    """Test cases for blockchain performance."""
    
    @pytest.mark.asyncio
    async def test_transaction_speed(self):
        """Test transaction processing speed."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.return_value = "fast_tx_hash"
            
            import time
            start_time = time.time()
            
            await solana_client.send_transaction({"amount": 1000})
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should be fast (under 1 second in test environment)
            assert processing_time < 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions(self):
        """Test handling of concurrent transactions."""
        solana_client = SolanaClient()
        
        with patch.object(solana_client, '_send_transaction') as mock_send:
            mock_send.return_value = "concurrent_tx_hash"
            
            # Create multiple concurrent transactions
            tasks = []
            for i in range(5):
                task = solana_client.send_transaction({"amount": i * 1000})
                tasks.append(task)
            
            # Execute all transactions concurrently
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 5
            assert all(result == "concurrent_tx_hash" for result in results)
