from fastapi import APIRouter
from typing import List

from utils.helpers import read_json
from schemas.seasons import SeasonPerformance

router = APIRouter()

@router.get("/seasons", response_model=List[SeasonPerformance])
def get_seasons():
    return read_json("seasons.json")
