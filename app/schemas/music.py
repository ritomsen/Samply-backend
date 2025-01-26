from pydantic import BaseModel
from typing import Optional


class MusicOutput(BaseModel):
    song: str
    artist: str
    img_url: Optional[str] = None
    # album: Optional[str] = None
    # released: Optional[str] = None

class MusicSample(BaseModel):
    song: str
    artist: str
    year: str
    img_url: Optional[str] = None
    element: Optional[str] = None

class OutputSamples(BaseModel):
    samples: list[MusicSample]
