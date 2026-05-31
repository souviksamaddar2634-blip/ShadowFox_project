from fastapi import APIRouter
from typing import List, Optional

from schemas.admin import QuizResponse
from services import admin_service

router = APIRouter()

@router.get("/quiz", response_model=List[QuizResponse])
def get_quiz(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """Retrieve trivia quiz questions from MongoDB."""
    return admin_service.get_quizzes(skip=skip, limit=limit, search=search)
