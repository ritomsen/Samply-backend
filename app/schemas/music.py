from pydantic import BaseModel
from typing import Optional

class MusicInput(BaseModel):
    title: str

class MusicOutput(BaseModel):
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    released: Optional[str] = None