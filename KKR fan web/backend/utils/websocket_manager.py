import sys
import json
from fastapi import WebSocket
from typing import Dict, Set, Any

from utils.logger import logger

# Reusable WebSocket Configuration Constants
MAX_CONNECTIONS = 500

class ConnectionManager:
    def __init__(self):
        # Keep track of active sockets per room using sets for O(1) lookups/removals
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "cheers": set(),
            "poll": set()
        }
        self.connection_count: int = 0

    async def connect(self, websocket: WebSocket, room: str) -> bool:
        """Connect and register a new WebSocket client if connection safeguards allow."""
        if self.connection_count >= MAX_CONNECTIONS:
            logger.warning(
                f"WebSocket connection rejected: Limit of {MAX_CONNECTIONS} active connections reached."
            )
            # 1008 is standard WS close code for Policy Violation
            await websocket.close(code=1008, reason="Connection limit exceeded")
            return False
            
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
            
        self.active_connections[room].add(websocket)
        self.connection_count += 1
        logger.info(
            f"WebSocket connection: Client registered to room '{room}'. "
            f"Room count: {len(self.active_connections[room])}, Total active: {self.connection_count}"
        )
        return True

    def disconnect(self, websocket: WebSocket, room: str):
        """Clean up and disconnect client registration."""
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            self.connection_count = max(0, self.connection_count - 1)
            logger.info(
                f"WebSocket connection: Client unregistered from room '{room}'. "
                f"Room count: {len(self.active_connections[room])}, Total active: {self.connection_count}"
            )

    async def broadcast(self, payload: Any, room: str):
        """Broadcast structured event message to all connected clients in the room."""
        if room not in self.active_connections or not self.active_connections[room]:
            return
            
        try:
            message_str = json.dumps(payload) if not isinstance(payload, str) else payload
        except Exception as e:
            logger.error(f"WebSocket broadcast: Failed to serialize payload: {e}")
            return
            
        # Log payload size
        payload_size = len(message_str.encode('utf-8'))
        logger.info(
            f"WebSocket broadcast: Sending to room '{room}'. "
            f"Active connections: {len(self.active_connections[room])}, Size: {payload_size} bytes."
        )
        
        # Async-safe iteration and transmission
        stale_connections = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"WebSocket broadcast: Failed to send to connection in room '{room}': {e}")
                stale_connections.append(connection)
                
        # Clean up stale connections identified during broadcast
        for connection in stale_connections:
            logger.info(f"WebSocket broadcast: Pruning stale socket connection from room '{room}'.")
            self.disconnect(connection, room)

    async def shutdown(self):
        """Gracefully close all WebSocket connections during server shutdown."""
        logger.info("WebSocket shutdown: Disconnecting all active client connections...")
        for room, connections in list(self.active_connections.items()):
            for ws in list(connections):
                try:
                    # 1001 is standard WS close code for Going Away
                    await ws.close(code=1001, reason="Server shutting down")
                except Exception:
                    pass
                self.disconnect(ws, room)
        logger.info("WebSocket shutdown: All active connections cleared.")

    def check_rate_limit(self, client_ip: str) -> bool:
        """
        Placeholder for rate-limiting spam protection.
        Can be wired to Redis IP key TTL thresholds.
        """
        return True

    async def publish_to_redis(self, event: str, payload: Dict[str, Any]):
        """
        Placeholder for Redis pub/sub pub-lisher.
        Enables multi-instance scaling for cluster/load-balancer configurations.
        """
        pass

# Global connection manager instance
manager = ConnectionManager()
