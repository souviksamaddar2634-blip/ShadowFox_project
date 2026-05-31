from fastapi import APIRouter

from schemas.poll import PollData, PollVote
from services import poll_service
from utils.websocket_manager import manager
from services.websocket_service import format_ws_event

router = APIRouter()

@router.get("/poll", response_model=PollData)
def get_poll():
    """Endpoint to retrieve current MVP poll results."""
    return poll_service.get_poll()

@router.post("/poll", response_model=PollData)
async def vote_poll(payload: PollVote):
    """Endpoint to submit a vote to the MVP poll."""
    updated_poll = poll_service.vote_poll(payload.index)
    event_payload = format_ws_event("poll_update", updated_poll)
    await manager.broadcast(event_payload, "poll")
    return updated_poll
