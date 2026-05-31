from fastapi import APIRouter
from typing import List, Dict, Optional

from utils.helpers import read_json
from schemas.admin import PlayerResponse
from schemas.players import StatEntry
from services import admin_service

router = APIRouter()

@router.get("/players", response_model=List[PlayerResponse])
def get_players(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None
):
    """Retrieve player profiles from MongoDB, supporting search, filters, and pagination."""
    return admin_service.get_players(skip=skip, limit=limit, search=search, role=role)

@router.get("/players/stats", response_model=Dict[str, List[StatEntry]])
def get_players_stats():
    """Retrieve detailed statistics from local JSON file (temporary JSON fallback)."""
    return read_json("stats.json")

@router.get("/stats", response_model=Dict[str, List[StatEntry]])
def get_stats():
    """Retrieve detailed statistics from local JSON file (temporary JSON fallback)."""
    return read_json("stats.json")
