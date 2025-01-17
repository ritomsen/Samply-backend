from pydantic import BaseModel
from typing import Optional


class MusicOutput(BaseModel):
    title: str
    artist: str
    related_tracks: list[str]
    # album: Optional[str] = None
    # released: Optional[str] = None