from fastapi import APIRouter, HTTPException
from ..schemas.music import MusicInput, MusicOutput
from ..services.music_service import fetch_music_data

router = APIRouter()

@router.get("/", response_model=MusicOutput)
async def get_music_data(title: str):
    """
    Example endpoint to get music data by title.
    """
    data = await fetch_music_data(title)
    if not data:
        raise HTTPException(status_code=404, detail="Music data not found.")
    return data

@router.post("/", response_model=MusicOutput)
async def analyze_music(input_data: MusicInput):
    """
    Example endpoint to analyze or do something with posted music data.
    """
    # Do some processing or call a service
    result = await fetch_music_data(input_data.title)
    if not result:
        raise HTTPException(status_code=404, detail="Music data not found.")
    return result
