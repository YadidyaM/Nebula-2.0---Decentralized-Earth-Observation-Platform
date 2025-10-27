from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Set
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent_connections: Dict[str, List[WebSocket]] = {}
        self.mission_connections: Dict[str, List[WebSocket]] = {}
        self.room_subscriptions: Dict[WebSocket, Set[str]] = {}  # websocket -> set of room_ids
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.room_subscriptions[websocket] = set()
        
        if client_id:
            if client_id not in self.agent_connections:
                self.agent_connections[client_id] = []
            self.agent_connections[client_id].append(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, client_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.room_subscriptions:
            del self.room_subscriptions[websocket]
        
        if client_id and client_id in self.agent_connections:
            if websocket in self.agent_connections[client_id]:
                self.agent_connections[client_id].remove(websocket)
            if not self.agent_connections[client_id]:
                del self.agent_connections[client_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_to_room(self, websocket: WebSocket, room_id: str):
        """Subscribe a connection to a specific room (mission, agent, etc.)"""
        if websocket in self.room_subscriptions:
            self.room_subscriptions[websocket].add(room_id)
            logger.info(f"WebSocket subscribed to room: {room_id}")
    
    async def unsubscribe_from_room(self, websocket: WebSocket, room_id: str):
        """Unsubscribe a connection from a specific room"""
        if websocket in self.room_subscriptions:
            self.room_subscriptions[websocket].discard(room_id)
            logger.info(f"WebSocket unsubscribed from room: {room_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: str):
        """Broadcast message to all active connections"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_room(self, message: str, room_id: str):
        """Broadcast message to all connections subscribed to a specific room"""
        disconnected = []
        for websocket, rooms in self.room_subscriptions.items():
            if room_id in rooms:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to room {room_id}: {e}")
                    disconnected.append(websocket)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_agent(self, message: str, agent_id: str):
        """Send message to all connections subscribed to a specific agent"""
        if agent_id in self.agent_connections:
            disconnected = []
            for connection in self.agent_connections[agent_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to agent {agent_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, agent_id)
    
    async def send_heartbeat(self):
        """Send heartbeat to all connections"""
        heartbeat = {
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat(),
            "active_connections": len(self.active_connections)
        }
        await self.broadcast(json.dumps(heartbeat))

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_agent":
                agent_id = message.get("agent_id")
                if agent_id:
                    await manager.connect(websocket, agent_id)
                    await manager.subscribe_to_room(websocket, f"agent_{agent_id}")
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscription_confirmed",
                            "agent_id": agent_id,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
            
            elif message.get("type") == "subscribe_mission":
                mission_id = message.get("mission_id")
                if mission_id:
                    await manager.subscribe_to_room(websocket, f"mission_{mission_id}")
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscription_confirmed",
                            "mission_id": mission_id,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
            
            elif message.get("type") == "unsubscribe":
                room_id = message.get("room_id")
                if room_id:
                    await manager.unsubscribe_from_room(websocket, room_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "unsubscription_confirmed",
                            "room_id": room_id,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
            
            elif message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
            
            elif message.get("type") == "agent_status_update":
                # Broadcast agent status update to all connected clients
                await manager.broadcast(data)
            
            elif message.get("type") == "mission_update":
                # Broadcast mission update to all connected clients
                await manager.broadcast(data)
            
            elif message.get("type") == "telemetry_update":
                # Broadcast telemetry update to all connected clients
                await manager.broadcast(data)
            
            elif message.get("type") == "risk_alert":
                # Broadcast risk alert to all connected clients
                await manager.broadcast(data)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.websocket("/agent/{agent_id}")
async def agent_websocket_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(websocket, agent_id)
    await manager.subscribe_to_room(websocket, f"agent_{agent_id}")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Add agent_id to message
            message["agent_id"] = agent_id
            message["timestamp"] = datetime.now().isoformat()
            
            # Broadcast to all connections subscribed to this agent
            await manager.broadcast_to_room(json.dumps(message), f"agent_{agent_id}")
            
            # Also broadcast to all connections for global updates
            await manager.broadcast(json.dumps(message))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)
    except Exception as e:
        logger.error(f"Agent WebSocket error: {e}")
        manager.disconnect(websocket, agent_id)

@router.websocket("/mission/{mission_id}")
async def mission_websocket_endpoint(websocket: WebSocket, mission_id: str):
    await manager.connect(websocket)
    await manager.subscribe_to_room(websocket, f"mission_{mission_id}")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Add mission_id to message
            message["mission_id"] = mission_id
            message["timestamp"] = datetime.now().isoformat()
            
            # Broadcast to all connections subscribed to this mission
            await manager.broadcast_to_room(json.dumps(message), f"mission_{mission_id}")
            
            # Also broadcast to all connections for global updates
            await manager.broadcast(json.dumps(message))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Mission WebSocket error: {e}")
        manager.disconnect(websocket)

# Utility functions for sending updates
async def send_agent_status_update(agent_id: str, status_data: Dict[str, Any]):
    """Send agent status update to all connected clients"""
    message = {
        "type": "agent_status_update",
        "agent_id": agent_id,
        "data": status_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(message))
    await manager.broadcast_to_room(json.dumps(message), f"agent_{agent_id}")

async def send_mission_update(mission_id: str, mission_data: Dict[str, Any]):
    """Send mission update to all connected clients"""
    message = {
        "type": "mission_update",
        "mission_id": mission_id,
        "data": mission_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(message))
    await manager.broadcast_to_room(json.dumps(message), f"mission_{mission_id}")

async def send_telemetry_update(agent_id: str, telemetry_data: Dict[str, Any]):
    """Send telemetry update to all connected clients"""
    message = {
        "type": "telemetry_update",
        "agent_id": agent_id,
        "data": telemetry_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(message))
    await manager.broadcast_to_room(json.dumps(message), f"agent_{agent_id}")

async def send_blockchain_update(transaction_data: Dict[str, Any]):
    """Send blockchain transaction update to all connected clients"""
    message = {
        "type": "blockchain_update",
        "data": transaction_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(message))

async def send_risk_alert(risk_data: Dict[str, Any]):
    """Send environmental risk alert to all connected clients"""
    message = {
        "type": "risk_alert",
        "data": risk_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(message))

# Background task to send periodic updates
async def send_periodic_updates():
    """Send periodic updates to keep connections alive and provide real-time data"""
    while True:
        try:
            # Send heartbeat to all connections
            await manager.send_heartbeat()
            
            # Wait 30 seconds before next update
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")
            await asyncio.sleep(30)

# Start background task when module is imported
asyncio.create_task(send_periodic_updates())