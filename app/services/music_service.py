import os
import requests
from typing import Optional, Dict
from shazamio import Shazam
from ..schemas.music import MusicOutput

# API_BASE_URL = "https://example-music-api.com"

# async def fetch_music_data(title: str) -> Optional[MusicOutput]:
#     """
#     Fetch music data from an external API or database.
#     For demonstration, this is a dummy function using requests.
#     """
#     try:
#         response = requests.get(f"{API_BASE_URL}/search", params={"title": title})
#         response.raise_for_status()
#         data = response.json()
        
#         # Map external data to our MusicOutput schema
#         music_info = MusicOutput(
#             title=data.get("title", title),
#             artist=data.get("artist"),
#             album=data.get("album"),
#             released=data.get("released")
#         )
#         return music_info
#     except requests.RequestException as e:
#         # Log exception or handle it as you see fit
#         print(f"Error fetching music data: {e}")
#         return None

async def recognize_song_via_shazam(audio_file_path: str) -> Dict:
    """
    Recognize a song using the shazamio library, given a file path.
    Returns the Shazam JSON response.
    """
    shazam = Shazam()
    try:
        # The 'recognize' method is an async method from shazamio that identifies audio
        out = await shazam.recognize(audio_file_path)
        return out
    except Exception as e:
        # Raise or handle the exception as needed
        raise RuntimeError(f"Error during Shazam recognition: {e}")

async def get_related_songs(track_id: int, limit: int = 5, offset: int = 0) -> Dict:
    """
    Fetch related tracks from Shazam.
    """
    shazam = Shazam()
    try:
        related = await shazam.related_tracks(track_id=track_id, limit=limit, offset=offset)
        return related
    except Exception as e:
        # Raise or handle the exception as needed
        raise RuntimeError(f"Error fetching related songs: {e}")