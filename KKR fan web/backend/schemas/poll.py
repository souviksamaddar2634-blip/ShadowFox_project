from pydantic import BaseModel, Field
from typing import List

class PollVote(BaseModel):
    index: int = Field(..., ge=0)

class PollData(BaseModel):
    votes: List[int]
    labels: List[str]
