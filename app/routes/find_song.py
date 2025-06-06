import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from ..schemas.music import MusicOutput, OutputSamples
from ..services.music_service import (
    recognize_song_via_shazam,
    scrape_page,
    scrape_sample_page
)


router = APIRouter()

@router.get("/")
async def get_music_data():
    """
    Example endpoint to get music data by title.
    """
    # data = await fetch_music_data(title)
    # if not data:
    #     raise HTTPException(status_code=404, detail="Music data not found.")
    return {"response": "TESTING"}

@router.post("/")
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

    song = recognition_result["title"]
    artist = recognition_result['artist']
    img_url = recognition_result['img_url']

    output = MusicOutput(song=song, artist=artist, img_url=img_url)
    # # 8. Optionally, fetch related songs
    # try:
    #     related_songs = await get_related_songs(track_id=track_id, limit=5, offset=0)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to fetch related songs: {str(e)}")

    return output

@router.get("/scrape-samples/")
async def scrape_samples(song_title: str, artist: str):
    """
    Scrape data from the web
    """
    # Try to scrape samples straight from guessing page name first, if it fails then try to get name from search page
    song = song_title
    artist = artist
    try:
        samples = await scrape_sample_page(song, artist)
    except Exception as e:
        raise HTTPException(
        status_code=404, 
        detail=f"No Samples Found: {str(e)}"
    )
    # Get the name and artist from the search page if the samples are not found
    if len(samples) == 0:
        try:
            data = await scrape_page(song, artist)
        except Exception as e:
            raise HTTPException(
            status_code=404, 
            detail=f"No Samples Found in Search Results, {str(e)}"
        )
        song = data['song']
        artist = data['artist']
        print(song,artist)
        try:
            samples = await scrape_sample_page(song, artist)
        except Exception as e:
            raise HTTPException(
            status_code=500, 
            detail=f"Failed to scrape samples: {str(e)}"
        )
    output = OutputSamples(samples=samples)
    return output
 

