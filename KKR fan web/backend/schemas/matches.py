from pydantic import BaseModel, Field
from typing import Optional

class MatchCreate(BaseModel):
    date: str = Field(..., min_length=1, description="Date of the match, e.g. 29 MAR 2026")
    opp: str = Field(..., min_length=1, description="Opponent name")
    venue: str = Field(..., min_length=1, description="Venue name")
    vs: str = Field(..., min_length=1, description="Opponent abbreviation code, e.g. MI")
    status: str = Field(..., min_length=1, description="Status code: won, lost, or noresult")
    desc: str = Field(..., min_length=1, description="Match description outcome description")
    theme: str = Field(..., min_length=1, description="Theme styling tag, e.g. background:#001f5b;color:#99cfff;border-color:#3a6abf")

class MatchUpdate(BaseModel):
    date: Optional[str] = Field(None, min_length=1)
    opp: Optional[str] = Field(None, min_length=1)
    venue: Optional[str] = Field(None, min_length=1)
    vs: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, min_length=1)
    desc: Optional[str] = Field(None, min_length=1)
    theme: Optional[str] = Field(None, min_length=1)

class MatchResponse(BaseModel):
    id: str
    date: str
    opp: str
    venue: str
    vs: str
    status: str
    desc: str
    theme: str
