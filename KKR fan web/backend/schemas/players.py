from pydantic import BaseModel
from typing import List

class StatEntry(BaseModel):
    k: str
    v: str

class Player(BaseModel):
    name: str
    jersey: int
    role: str
    country: str
    bio: str
    stats: List[StatEntry]
    image: str
