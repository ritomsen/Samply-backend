import os
import time
import requests
import re
from typing import Optional, Dict
from shazamio import Shazam
from ..schemas.music import MusicOutput
import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from playwright.async_api import async_playwright

async def recognize_song_via_shazam(audio_file_path: str) -> Dict:
    """
    Recognize a song using the shazamio library, given a file path.
    Returns the Shazam JSON response.
    """
    shazam = Shazam()
    try:
        out = await shazam.recognize(audio_file_path)
        # print(out)
        if len(out["matches"]) == 0:
            raise RuntimeError(f"No Matches {e}") 
        else:
            top_match = out["track"]
            title = top_match["title"]
            artist = top_match["subtitle"]
            cover_art = top_match["images"]["coverart"]
            print(title, artist, cover_art)
            return {"title": title, "artist": artist, "img_url": cover_art}
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
    


async def scrape_page(song_title: str, artist: str) -> dict:
    """
    Launches a headless Chromium browser and scrapes the 
    'a.trackTitle' text on whosampled.com.
    """
    # 1. Build the search URL
    query = song_title.replace(" ", "-")
    url = f"https://www.whosampled.com/search/tracks/?q={query}"

    # 2. Launch Playwright
    async with async_playwright() as p:
        # Launch headless Chromium
        browser = await p.chromium.launch(headless=True)
        
        # Optional: Provide a more "browser-like" user agent
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        )
        
        page = await context.new_page()
        
        # 3. Navigate to the site
        print(url)
        await page.goto(url)
        
        
        # 5. Extract the text from the first matching element
        # Option A: direct method on the locator
        element = page.locator("a.trackName", has_text=f"{song_title}").first
        await element.wait_for(timeout=10000);

        element_text = await element.inner_text() 

        artist = page.locator("span.trackArtist", has_text=f"{artist}").first.locator("a").first
        await artist.wait_for(timeout=10000);
        
        song_artist = await artist.inner_text()
        
        # 6. Close the browser
        await browser.close()

    # 7. Return scraped info
    return {"song": element_text.strip() if element_text else None, "artist": song_artist.strip() if song_artist else None}

async def scrape_sample_page(song_title: str, artist: str) -> dict:
    a, t = artist.replace(" ", "-"), song_title.replace(" ", "-")
    url = f"https://www.whosampled.com/{a}/{t}"
    print(url)
        # 2. Launch Playwright
    async with async_playwright() as p:
        # Launch headless Chromium
        browser = await p.chromium.launch(headless=True)
        
        # Optional: Provide a more "browser-like" user agent
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        )
        
        page = await context.new_page()
        
        await page.goto(url)
        
        # WHAT IF JUST ONE SONG
        samples = page.locator("section.subsection", has_text="Contains samples").first
        await samples.wait_for(timeout=10000);
        
        parsed_samples = await samples.inner_text()

        # 6. Close the browser
        await browser.close()

        # s = []
        pattern = r'\n\s*\n\s*(.*?)\n\s*\t(.*?)\t([^\t]*)\t'
        
        # Find all matches
        matches = re.findall(pattern, parsed_samples)
        
        # Create the desired list format
        # 7. Return scraped info
        return [
            {"song": song.strip(), "artist": artist.strip(), "year": year.strip()}
            for song, artist, year in matches
        ]
