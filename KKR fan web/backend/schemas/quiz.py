from pydantic import BaseModel
from typing import List

class QuizQuestion(BaseModel):
    q: str
    opts: List[str]
    ans: int
    exp: str
