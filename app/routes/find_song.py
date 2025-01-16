import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from ..schemas.music import MusicInput, MusicOutput
from ..services.music_service import (
    fetch_music_data,
    recognize_song_via_shazam,
    get_related_songs
)

router = APIRouter()

# @router.get("/", response_model=Optional[MusicOutput])
# async def get_music_data(title: str):
#     """
#     Example endpoint to get music data by title.
#     """
#     data = await fetch_music_data(title)
#     if not data:
#         raise HTTPException(status_code=404, detail="Music data not found.")
#     return data

@router.post("/recognize")
async def recognize_song(file: UploadFile = File(...)):
    """
    Receives an audio file from the client, saves it temporarily,
    recognizes it with Shazam, and returns the recognized track data.
    """
    # 1. Validate file content type (basic check)
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio type.")

    # 2. Generate a unique filename to avoid collisions
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_filepath = os.path.join("/tmp", temp_filename)

    # 3. Save file to disk
    try:
        with open(temp_filepath, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    # 4. Call Shazam to recognize the song
    try:
        recognition_result = await recognize_song_via_shazam(temp_filepath)
    except Exception as e:
        # Cleanup the file if something went wrong
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=500, detail=f"Shazam recognition failed: {str(e)}")

    # 5. Cleanup the file after we're done
    if os.path.exists(temp_filepath):
        os.remove(temp_filepath)

    # 6. Extract track ID from the result
    #    The exact structure of recognition_result can vary depending on Shazam response
    matches = recognition_result.get("matches", [])
    if not matches:
        raise HTTPException(status_code=404, detail="No matches found in Shazam response.")

    track_id_str = matches[0].get("id", "")
    if not track_id_str:
        raise HTTPException(status_code=404, detail="No track ID found in Shazam response.")

    # 7. Validate/convert track ID
    try:
        track_id = int(track_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid track ID format from Shazam.")

    # 8. Optionally, fetch related songs
    try:
        related_songs = await get_related_songs(track_id=track_id, limit=5, offset=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch related songs: {str(e)}")

    return {
        "recognition_result": recognition_result,
        "track_id": track_id,
        "related_songs": related_songs,
    }
