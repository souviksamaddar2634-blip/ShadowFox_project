from fastapi import APIRouter
from typing import List, Optional

from schemas.admin import LegendResponse
from services import admin_service

router = APIRouter()

@router.get("/legends", response_model=List[LegendResponse])
def get_legends(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """Retrieve Hall of Fame legends from MongoDB."""
    return admin_service.get_legends(skip=skip, limit=limit, search=search)
