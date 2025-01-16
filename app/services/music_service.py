import requests
from typing import Optional
from ..schemas.music import MusicOutput

API_BASE_URL = "https://example-music-api.com"

async def fetch_music_data(title: str) -> Optional[MusicOutput]:
    """
    Fetch music data from an external API or database.
    For demonstration, this is a dummy function using requests.
    """
    # Example of calling an external API
    # Adjust this to the actual music service URL
    try:
        response = requests.get(f"{API_BASE_URL}/search", params={"title": title})
        response.raise_for_status()
        data = response.json()
        
        # Map external data to our MusicOutput schema
        music_info = MusicOutput(
            title=data.get("title", title),
            artist=data.get("artist"),
            album=data.get("album"),
            released=data.get("released")
        )
        return music_info
    except requests.RequestException:
        return None
