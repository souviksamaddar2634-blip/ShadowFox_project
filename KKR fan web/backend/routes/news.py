from fastapi import APIRouter
from typing import List, Optional

from schemas.news import NewsResponse
from services import news_service

router = APIRouter()

@router.get("/news", response_model=List[NewsResponse])
def get_news(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    cat: Optional[str] = None
):
    """Retrieve news articles from MongoDB, supporting search, filters, and pagination."""
    return news_service.get_news(skip=skip, limit=limit, search=search, cat=cat)
