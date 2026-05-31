import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional

from utils.websocket_manager import manager
from services.websocket_service import authenticate_websocket, serialize_ws_error
from utils.logger import logger

router = APIRouter()

async def handle_websocket_room(websocket: WebSocket, room: str, token: Optional[str] = None):
    """
    Common handler for WebSocket connection lifespans.
    Supports JWT auth, connection limits, heartbeat timeout checks, and stale connection pruning.
    """
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"WebSocket: Handshake request from '{client_ip}' for room '{room}'")
    
    # Optional JWT token auth check
    if token:
        is_authed = authenticate_websocket(token)
        if not is_authed:
            logger.warning(f"WebSocket: Handshake auth failed for '{client_ip}' in room '{room}'")
            await websocket.accept()
            await websocket.send_json(serialize_ws_error(4001, "Invalid or expired JWT token"))
            await websocket.close(code=4001, reason="Unauthorized")
            return
            
    # Establish connection
    success = await manager.connect(websocket, room)
    if not success:
        return
        
    try:
        while True:
            # Enforce 35 second timeout for heartbeats
            try:
                # Wait for text messages from client (pings/heartbeats)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=35.0)
                
                # Check for ping heartbeat
                if message == "ping":
                    await websocket.send_text(json.dumps({"event": "pong"}))
                    logger.debug(f"WebSocket: Ping-pong heartbeat exchanged with '{client_ip}' in room '{room}'")
                else:
                    # Log other client inputs if any
                    logger.info(f"WebSocket: Received message from client '{client_ip}' in room '{room}': {message}")
            except asyncio.TimeoutError:
                # Clean up inactive/stale sockets
                logger.warning(f"WebSocket: Heartbeat timeout from client '{client_ip}' in room '{room}'. Disconnecting.")
                await websocket.close(code=1000, reason="Heartbeat timeout")
                break
    except WebSocketDisconnect:
        logger.info(f"WebSocket: Client '{client_ip}' disconnected gracefully from room '{room}'")
        manager.disconnect(websocket, room)
    except Exception as e:
        logger.error(f"WebSocket: Error in connection for client '{client_ip}' in room '{room}': {e}")
        manager.disconnect(websocket, room)

@router.websocket("/ws/cheers")
async def ws_cheers(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket room for real-time cheers updates."""
    await handle_websocket_room(websocket, "cheers", token)

@router.websocket("/ws/poll")
async def ws_poll(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket room for real-time MVP poll updates."""
    await handle_websocket_room(websocket, "poll", token)
