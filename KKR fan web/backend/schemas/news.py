from pydantic import BaseModel, Field
from typing import Optional

class NewsCreate(BaseModel):
    cat: str = Field(..., min_length=1, description="Category of the news article")
    headline: str = Field(..., min_length=1, description="Headline of the article")
    snippet: str = Field(..., min_length=1, description="Brief snippet text")
    date: Optional[str] = Field(None, description="Display date (defaults to UTC date on creation)")
    link: Optional[str] = Field("#", description="External url link")

class NewsUpdate(BaseModel):
    cat: Optional[str] = Field(None, min_length=1)
    headline: Optional[str] = Field(None, min_length=1)
    snippet: Optional[str] = Field(None, min_length=1)
    date: Optional[str] = None
    link: Optional[str] = None

class NewsResponse(BaseModel):
    id: str
    date: str
    cat: str
    headline: str
    snippet: str
    link: str
