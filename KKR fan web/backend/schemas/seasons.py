from pydantic import BaseModel

class SeasonPerformance(BaseModel):
    year: str
    w: int
    l: int
    title: bool
