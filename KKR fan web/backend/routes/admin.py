from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict

from utils.permissions import require_admin
# Schemas
from schemas.news import NewsCreate, NewsUpdate, NewsResponse
from schemas.matches import MatchCreate, MatchUpdate, MatchResponse
from schemas.admin import (
    PlayerCreate, PlayerUpdate, PlayerResponse,
    QuizCreate, QuizUpdate, QuizResponse,
    LegendCreate, LegendUpdate, LegendResponse
)
# Services
from services import news_service, matches_service, admin_service

router = APIRouter()

# --- News Management Endpoints ---
@router.post("/news", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(payload: NewsCreate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Create a news article (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    return news_service.create_news(payload, admin_name)

@router.put("/news/{id}", response_model=NewsResponse)
def update_news(id: str, payload: NewsUpdate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Update a news article (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    res = news_service.update_news(id, payload, admin_name)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found.")
    return res

@router.delete("/news/{id}", status_code=status.HTTP_200_OK)
def delete_news(id: str, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Delete a news article (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    success = news_service.delete_news(id, admin_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found.")
    return {"status": "success", "message": "News article deleted successfully."}


# --- Player Management Endpoints ---
@router.post("/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Create a player profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    return admin_service.create_player(payload, admin_name)

@router.put("/players/{id}", response_model=PlayerResponse)
def update_player(id: str, payload: PlayerUpdate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Update a player profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    res = admin_service.update_player(id, payload, admin_name)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found.")
    return res

@router.delete("/players/{id}", status_code=status.HTTP_200_OK)
def delete_player(id: str, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Delete a player profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    success = admin_service.delete_player(id, admin_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found.")
    return {"status": "success", "message": "Player profile deleted successfully."}


# --- Match Management Endpoints ---
@router.post("/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(payload: MatchCreate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Create a match record (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    return matches_service.create_match(payload, admin_name)

@router.put("/matches/{id}", response_model=MatchResponse)
def update_match(id: str, payload: MatchUpdate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Update a match record (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    res = matches_service.update_match(id, payload, admin_name)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match record not found.")
    return res

@router.delete("/matches/{id}", status_code=status.HTTP_200_OK)
def delete_match(id: str, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Delete a match record (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    success = matches_service.delete_match(id, admin_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match record not found.")
    return {"status": "success", "message": "Match record deleted successfully."}


# --- Quiz Management Endpoints ---
@router.post("/quiz", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(payload: QuizCreate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Create a trivia quiz question (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    return admin_service.create_quiz(payload, admin_name)

@router.put("/quiz/{id}", response_model=QuizResponse)
def update_quiz(id: str, payload: QuizUpdate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Update a trivia quiz question (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    res = admin_service.update_quiz(id, payload, admin_name)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz question not found.")
    return res

@router.delete("/quiz/{id}", status_code=status.HTTP_200_OK)
def delete_quiz(id: str, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Delete a trivia quiz question (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    success = admin_service.delete_quiz(id, admin_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz question not found.")
    return {"status": "success", "message": "Quiz question deleted successfully."}


# --- Legends Management Endpoints ---
@router.post("/legends", response_model=LegendResponse, status_code=status.HTTP_201_CREATED)
def create_legend(payload: LegendCreate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Create a Hall of Fame legend profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    return admin_service.create_legend(payload, admin_name)

@router.put("/legends/{id}", response_model=LegendResponse)
def update_legend(id: str, payload: LegendUpdate, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Update a Hall of Fame legend profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    res = admin_service.update_legend(id, payload, admin_name)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legend profile not found.")
    return res

@router.delete("/legends/{id}", status_code=status.HTTP_200_OK)
def delete_legend(id: str, current_admin: Dict[str, Any] = Depends(require_admin)):
    """Delete a Hall of Fame legend profile (Admin-only)."""
    admin_name = current_admin.get("username", "admin")
    success = admin_service.delete_legend(id, admin_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legend profile not found.")
    return {"status": "success", "message": "Legend profile deleted successfully."}
