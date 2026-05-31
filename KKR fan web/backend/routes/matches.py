from fastapi import APIRouter
from typing import List, Optional

from schemas.matches import MatchResponse
from services import matches_service

router = APIRouter()

@router.get("/matches", response_model=List[MatchResponse])
def get_matches(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Retrieve match records from MongoDB, supporting search, filters, and pagination."""
    return matches_service.get_matches(skip=skip, limit=limit, search=search, status=status)
