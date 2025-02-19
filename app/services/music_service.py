import math
import re
from typing import Dict
from shazamio import Shazam
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
    Searches for a song on whosampled.com and returns the best matching result.

    Args:
        song_title (str): The title of the song to search for
        artist (str): The artist name to search for

    Returns:
        dict: A dictionary containing the matched song title and artist
            {
                "song": str,  # The matched song title
                "artist": str # The matched artist name
            }

    Raises:
        ValueError: If no matching song and artist are found in search results
    """
    # Take out features from song title and turn into url query parameter
    cleaned_song_title = song_title.split('(')[0].strip()
    search_query = f"{cleaned_song_title.replace(' ', '%20')}"
    search_url = f"https://www.whosampled.com/search/tracks/?q={search_query}"

    # search result variables
    matched_artist = ""
    matched_title = ""

    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        print(search_url)
        await page.goto(search_url)

        # see if search result artist match shazam artist
        artist_elements = await page.locator("span.trackArtist").all()
        artist_match_index = -1
        for index, artist_element in enumerate(artist_elements):
            search_result_artist = await artist_element.locator("a").first.inner_text()
            if artist.lower() in search_result_artist.lower() or search_result_artist.lower() in artist.lower():
                matched_artist = search_result_artist
                artist_match_index = index
                break
        
        track_elements = await page.locator("a.trackName").all()
        # if search result artist matches shazam artist then just match track name
        if artist_match_index != -1:
            matched_title = await track_elements[artist_match_index].inner_text()
        else: #Else look for track name match then match artist
            title_match_index = -1
            for index, track in enumerate(track_elements):
                track_title = await track.inner_text()
                if cleaned_song_title.lower() in track_title.lower() or track_title.lower() in cleaned_song_title.lower():
                    matched_title = track_title
                    title_match_index = index
                    break
            if title_match_index != -1:
                matched_artists = await artist_elements[title_match_index].locator("a").all()
                first_artist = await matched_artists[0].inner_text()
                for a in matched_artists:
                    a_name = await a.inner_text()
                    if a_name.lower() in artist.lower() or artist.lower() in a_name.lower():
                        matched_artist = first_artist
        await browser.close()
    # Return error if no match found
    if not matched_artist or not matched_title:
        raise ValueError("Could not find matching song and artist in search results")
    # Return search results
    return {"song": matched_title.strip(), "artist": matched_artist.strip()}

async def scrape_sample_page(song_title: str, artist: str) -> dict:
    """
    Scrapes a song's page on whosampled.com to get all samples used in the song.

    Args:
        song_title (str): The title of the song to get samples for
        artist (str): The artist name of the song

    Returns:
        list: A list of dictionaries containing sample information
            [{
                "song": str,     # The title of the sampled song
                "artist": str,   # The artist of the sampled song
                "year": str,     # The release year of the sampled song
                "element": str,  # What element was sampled (e.g. "Drums", "Vocals")
                "img_url": str   # URL to the album art image
            }]

    Raises:
        Exception: If the samples section cannot be found on the page
    """
    # Prepare url
    a, t = artist.replace(" ", "-"), song_title.replace(" ", "-")
    url = f"https://www.whosampled.com/{a}/{t}/"
    print(url)
   
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        await page.goto(url)

        # If page redirects then exit
        if page.url != url:
            print(page.url)
            await browser.close()
            return []
       
        try:
            # See if this is a real page with samples
            samples = page.locator("section.subsection", has_text="Contains samples").first
            await samples.wait_for(timeout=10000)
        except Exception as err:
            not_found = await page.locator("h1.heading", has_text="Page Not Found").inner_text()
            if not_found:
                return []



        # Get img links
        img_elements = await samples.locator("img").all()
        img_urls = []
        for img in img_elements:
            src = await img.get_attribute('src')
            img_urls.append(src)

        # Get the text version of samples
        parsed_samples = await samples.inner_text()

        # Get number of samples amount total (not just on page)
        pattern = r'Contains samples of (\d+) songs'
        num_samples = re.search(pattern, parsed_samples, re.IGNORECASE)
        if num_samples:
            num_samples = int(num_samples.group(1))
        else:
            num_samples = 0

        await browser.close() # Close Browser

        # If more than 3 samples than have to go to samples page to get the rest
        if num_samples > 3:
            # 16 samples per page
            num_pages = math.ceil(num_samples / 16.0)
            # Result samples and img urls
            page_texts = []
            img_urls = []

            # Go to each page and open page and scrape samples
            for pg in range(1, num_pages+1):
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/109.0.0.0 Safari/537.36"
                        )
                )
                url = f"https://www.whosampled.com/{a}/{t}/samples/?cp={pg}"
                print(url)
                page = await context.new_page()
                await page.goto(url)
                try:
                    
                    s = page.locator("tbody").first
                    await s.wait_for(timeout=10000);

                    page_texts.append(await s.inner_text())
                    img_elements = await s.locator("img").all()
                    for img in img_elements:
                        src = await img.get_attribute('src')
                        img_urls.append(src)
                except Exception as e:
                    print(f"Error getting samples data from samples page: {str(e)}")
                    raise
                await browser.close()

            parsed_samples = '\n'.join(page_texts) # Join each page of samples together

    # Regex the text to get the samples and turn into json
    pattern = r'\s*\n\s*(.*?)\n\s*\t(.*?)\t([^\t]*)\t(.*?)'
    matches = re.findall(pattern, parsed_samples)
    output = []
    for i in range(len(matches)):
        output.append({"song": matches[i][0].strip(), "artist": matches[i][1].strip(), "year": matches[i][2].strip(), "element": matches[i][3].strip(), "img_url": "https://www.whosampled.com" + img_urls[i]})

    return output
