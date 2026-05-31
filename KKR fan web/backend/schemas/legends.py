from pydantic import BaseModel

class LegendProfile(BaseModel):
    name: str
    years: str
    achievement: str
    stat: str
    avatar: str
