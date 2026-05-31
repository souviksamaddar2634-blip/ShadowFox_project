from typing import Any, Dict
from utils.auth import verify_token
from utils.logger import logger

def format_ws_event(event: str, data: Any) -> Dict[str, Any]:
    """Wraps payload data into a structured WebSocket event envelope."""
    return {
        "event": event,
        "data": data
    }

def serialize_ws_error(code: int, message: str) -> Dict[str, Any]:
    """Serialize a WebSocket error into a consistent JSON schema."""
    return {
        "event": "error",
        "error": {
            "code": code,
            "message": message
        }
    }

def authenticate_websocket(token: str) -> bool:
    """
    WebSocket authentication hook.
    Verifies JWT Bearer token claims prior to handshake completion.
    """
    if not token:
        return False
    try:
        verify_token(token)
        return True
    except Exception as e:
        logger.warning(f"WebSocket auth handshake: Token verification failed: {e}")
        return False
