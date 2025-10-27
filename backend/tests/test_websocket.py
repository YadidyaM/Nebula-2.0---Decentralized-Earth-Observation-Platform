"""
Tests for WebSocket functionality
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.api.v1.endpoints.websocket import ConnectionManager, router
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.websocket
class TestConnectionManager:
    """Test cases for WebSocket connection manager."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self, connection_manager):
        """Test connection manager initialization."""
        assert connection_manager.active_connections == []
        assert connection_manager.room_subscriptions == {}
    
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, connection_manager):
        """Test WebSocket connection and disconnection."""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.client.host = "127.0.0.1"
        
        # Test connection
        await connection_manager.connect(mock_websocket)
        assert len(connection_manager.active_connections) == 1
        assert mock_websocket in connection_manager.active_connections
        
        # Test disconnection
        await connection_manager.disconnect(mock_websocket)
        assert len(connection_manager.active_connections) == 0
        assert mock_websocket not in connection_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, connection_manager):
        """Test broadcasting messages to all connections."""
        # Create mock connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        
        # Connect both
        await connection_manager.connect(mock_websocket1)
        await connection_manager.connect(mock_websocket2)
        
        # Broadcast message
        message = {"type": "test", "data": "test message"}
        await connection_manager.broadcast(message)
        
        # Verify both connections received the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_room_subscription(self, connection_manager):
        """Test room-based message subscription."""
        # Create mock connection
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Subscribe to room
        room_id = "mission_123"
        await connection_manager.subscribe_to_room(mock_websocket, room_id)
        
        assert room_id in connection_manager.room_subscriptions
        assert mock_websocket in connection_manager.room_subscriptions[room_id]
        
        # Unsubscribe from room
        await connection_manager.unsubscribe_from_room(mock_websocket, room_id)
        assert room_id not in connection_manager.room_subscriptions
    
    @pytest.mark.asyncio
    async def test_room_broadcast(self, connection_manager):
        """Test broadcasting messages to specific rooms."""
        # Create mock connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        
        # Connect both
        await connection_manager.connect(mock_websocket1)
        await connection_manager.connect(mock_websocket2)
        
        # Subscribe to different rooms
        await connection_manager.subscribe_to_room(mock_websocket1, "room_1")
        await connection_manager.subscribe_to_room(mock_websocket2, "room_2")
        
        # Broadcast to room_1
        message = {"type": "room_message", "data": "room 1 message"}
        await connection_manager.broadcast_to_room("room_1", message)
        
        # Only websocket1 should receive the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_heartbeat(self, connection_manager):
        """Test heartbeat functionality."""
        # Create mock connection
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Send heartbeat
        await connection_manager.send_heartbeat()
        
        # Verify heartbeat was sent
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        message_data = json.loads(sent_message)
        assert message_data["type"] == "heartbeat"
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, connection_manager):
        """Test handling of connection errors."""
        # Create mock connection that raises an exception
        mock_websocket = AsyncMock()
        mock_websocket.send_text.side_effect = Exception("Connection error")
        
        await connection_manager.connect(mock_websocket)
        
        # Broadcasting should handle the error gracefully
        message = {"type": "test", "data": "test message"}
        await connection_manager.broadcast(message)
        
        # Connection should be removed due to error
        assert mock_websocket not in connection_manager.active_connections

@pytest.mark.websocket
class TestWebSocketEndpoints:
    """Test cases for WebSocket endpoints."""
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is properly configured."""
        # Check that the WebSocket router is included
        assert router is not None
        
        # Check that the endpoint exists
        routes = [route.path for route in router.routes]
        assert "/ws" in routes or "/websocket" in routes
    
    @pytest.mark.asyncio
    async def test_websocket_connection_flow(self):
        """Test WebSocket connection flow."""
        # This would require a more complex test setup with actual WebSocket client
        # For now, we'll test the basic structure
        
        # Test that the connection manager is properly initialized
        manager = ConnectionManager()
        assert manager is not None
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'broadcast')
        assert hasattr(manager, 'subscribe_to_room')
        assert hasattr(manager, 'unsubscribe_from_room')
        assert hasattr(manager, 'broadcast_to_room')

@pytest.mark.websocket
class TestWebSocketMessageHandling:
    """Test cases for WebSocket message handling."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_message_types(self, connection_manager):
        """Test different message types."""
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Test different message types
        message_types = [
            "mission_update",
            "agent_status",
            "telemetry_data",
            "risk_alert",
            "system_notification"
        ]
        
        for msg_type in message_types:
            message = {
                "type": msg_type,
                "data": f"Test {msg_type} message",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            await connection_manager.broadcast(message)
            mock_websocket.send_text.assert_called()
            mock_websocket.reset_mock()
    
    @pytest.mark.asyncio
    async def test_message_format_validation(self, connection_manager):
        """Test message format validation."""
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Test valid message format
        valid_message = {
            "type": "test",
            "data": "test data",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        await connection_manager.broadcast(valid_message)
        mock_websocket.send_text.assert_called_once()
        
        # Verify the message was properly formatted as JSON
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "test"
        assert parsed_message["data"] == "test data"
    
    @pytest.mark.asyncio
    async def test_large_message_handling(self, connection_manager):
        """Test handling of large messages."""
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Create a large message
        large_data = "x" * 10000  # 10KB of data
        large_message = {
            "type": "large_data",
            "data": large_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Should handle large messages without issues
        await connection_manager.broadcast(large_message)
        mock_websocket.send_text.assert_called_once()

@pytest.mark.websocket
class TestWebSocketRoomManagement:
    """Test cases for WebSocket room management."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_multiple_room_subscriptions(self, connection_manager):
        """Test subscribing to multiple rooms."""
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Subscribe to multiple rooms
        rooms = ["mission_123", "agent_456", "telemetry_789"]
        
        for room in rooms:
            await connection_manager.subscribe_to_room(mock_websocket, room)
        
        # Verify all subscriptions
        for room in rooms:
            assert room in connection_manager.room_subscriptions
            assert mock_websocket in connection_manager.room_subscriptions[room]
    
    @pytest.mark.asyncio
    async def test_room_cleanup_on_disconnect(self, connection_manager):
        """Test that rooms are cleaned up when connection disconnects."""
        mock_websocket = AsyncMock()
        await connection_manager.connect(mock_websocket)
        
        # Subscribe to room
        room_id = "test_room"
        await connection_manager.subscribe_to_room(mock_websocket, room_id)
        
        # Disconnect
        await connection_manager.disconnect(mock_websocket)
        
        # Room should be cleaned up
        assert room_id not in connection_manager.room_subscriptions
    
    @pytest.mark.asyncio
    async def test_room_broadcast_multiple_subscribers(self, connection_manager):
        """Test broadcasting to rooms with multiple subscribers."""
        # Create multiple connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Connect all
        await connection_manager.connect(mock_websocket1)
        await connection_manager.connect(mock_websocket2)
        await connection_manager.connect(mock_websocket3)
        
        # Subscribe to same room
        room_id = "shared_room"
        await connection_manager.subscribe_to_room(mock_websocket1, room_id)
        await connection_manager.subscribe_to_room(mock_websocket2, room_id)
        # websocket3 is not subscribed to this room
        
        # Broadcast to room
        message = {"type": "room_broadcast", "data": "shared message"}
        await connection_manager.broadcast_to_room(room_id, message)
        
        # Only subscribed connections should receive the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_called_once()
        mock_websocket3.send_text.assert_not_called()

@pytest.mark.websocket
class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_with_real_time_data(self):
        """Test WebSocket with real-time data simulation."""
        manager = ConnectionManager()
        
        # Simulate real-time data flow
        mock_websocket = AsyncMock()
        await manager.connect(mock_websocket)
        
        # Subscribe to telemetry room
        await manager.subscribe_to_room(mock_websocket, "telemetry")
        
        # Simulate telemetry data updates
        telemetry_data = {
            "type": "telemetry_data",
            "data": {
                "agent_id": "test_agent",
                "timestamp": "2024-01-01T00:00:00Z",
                "position": {"lat": 40.7128, "lng": -74.0060, "alt": 700},
                "environmental_data": {"temperature": 25.5, "humidity": 80}
            }
        }
        
        await manager.broadcast_to_room("telemetry", telemetry_data)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed_message = json.loads(sent_message)
        assert parsed_message["type"] == "telemetry_data"
        assert parsed_message["data"]["agent_id"] == "test_agent"
    
    @pytest.mark.asyncio
    async def test_websocket_error_recovery(self):
        """Test WebSocket error recovery mechanisms."""
        manager = ConnectionManager()
        
        # Create connection that will fail
        mock_websocket = AsyncMock()
        mock_websocket.send_text.side_effect = Exception("Network error")
        
        await manager.connect(mock_websocket)
        
        # Try to broadcast - should handle error gracefully
        message = {"type": "test", "data": "test"}
        await manager.broadcast(message)
        
        # Connection should be removed due to error
        assert mock_websocket not in manager.active_connections
        
        # Create new connection
        new_mock_websocket = AsyncMock()
        await manager.connect(new_mock_websocket)
        
        # Should work normally now
        await manager.broadcast(message)
        new_mock_websocket.send_text.assert_called_once()
