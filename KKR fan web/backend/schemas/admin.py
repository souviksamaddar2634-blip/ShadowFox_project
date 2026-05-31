from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.players import StatEntry

# Player CRUD Validation Schemas
class PlayerCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the player")
    jersey: int = Field(..., ge=0, description="Jersey number")
    role: str = Field(..., min_length=1, description="Player role, e.g. Batter, Bowler, All-rounder")
    country: str = Field(..., min_length=1, description="Country nationality")
    bio: str = Field(..., min_length=1, description="Player biographical summary")
    stats: List[StatEntry] = Field(default=[], description="List of key-value stat pairs")
    image: str = Field("", description="Path to player image, e.g. images/player-name.jpg")

class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    jersey: Optional[int] = Field(None, ge=0)
    role: Optional[str] = Field(None, min_length=1)
    country: Optional[str] = Field(None, min_length=1)
    bio: Optional[str] = Field(None, min_length=1)
    stats: Optional[List[StatEntry]] = None
    image: Optional[str] = None

class PlayerResponse(BaseModel):
    id: str
    name: str
    jersey: int
    role: str
    country: str
    bio: str
    stats: List[StatEntry]
    image: str

# Quiz CRUD Validation Schemas
class QuizCreate(BaseModel):
    q: str = Field(..., min_length=1, description="Quiz trivia question")
    opts: List[str] = Field(..., description="List of multiple-choice options")
    ans: int = Field(..., ge=0, description="0-indexed integer option matching the correct answer")
    exp: str = Field(..., min_length=1, description="Explanation text explaining the answer context")

class QuizUpdate(BaseModel):
    q: Optional[str] = Field(None, min_length=1)
    opts: Optional[List[str]] = None
    ans: Optional[int] = Field(None, ge=0)
    exp: Optional[str] = Field(None, min_length=1)

class QuizResponse(BaseModel):
    id: str
    q: str
    opts: List[str]
    ans: int
    exp: str

# Legend CRUD Validation Schemas
class LegendCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the legend")
    years: str = Field(..., min_length=1, description="Active years, e.g. 2008 – 2010")
    achievement: str = Field(..., min_length=1, description="Achieved milestone summary")
    stat: str = Field(..., min_length=1, description="Historical summary stat label")
    avatar: str = Field("", description="Path to legend avatar image, e.g. images/legend-name.jpg")

class LegendUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    years: Optional[str] = Field(None, min_length=1)
    achievement: Optional[str] = Field(None, min_length=1)
    stat: Optional[str] = Field(None, min_length=1)
    avatar: Optional[str] = None

class LegendResponse(BaseModel):
    id: str
    name: str
    years: str
    achievement: str
    stat: str
    avatar: str
