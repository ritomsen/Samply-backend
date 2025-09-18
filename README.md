## Sample Finder Backend (FastAPI)

FastAPI backend that:

- Accepts a short audio clip and identifies the song using Shazam (via `shazamio`).
- Scrapes WhoSampled to list songs sampled in the identified track (via Playwright).
- Provides Spotify OAuth login and a simple profile/top-tracks fetch using `spotipy`.

The service exposes OpenAPI docs at `/docs` and `/redoc` when running locally.

---

### Tech Stack
- **Framework**: FastAPI (Starlette under the hood)
- **Auth**: Spotify OAuth (Spotipy)
- **Audio Recognition**: Shazam (`shazamio`)
- **Scraping**: Playwright (Chromium)
- **Config**: `python-dotenv`

---

### Requirements
- Python 3.10+
- pip (or uv/pipx)
- Playwright browsers (Chromium) installed for scraping

---

### Quick Start
1) Create and activate a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
# Base requirements
pip install -r requirements.txt

# Additional runtime deps used by the code (not listed in requirements.txt):
pip install shazamio spotipy playwright

# Install Playwright browsers (Chromium is required by this project)
python -m playwright install chromium
```

3) Create `.env`

```bash
cp .env.example .env # if you create one; otherwise create manually
```

Or create the file with at least the following variables:

```env
# Used by Starlette sessions. Set to a long random string.
SESSION_SECRET_KEY=change-me

# Spotify OAuth (create an app at https://developer.spotify.com/)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/callback

# Where to send users after successful Spotify login
FRONTEND_REDIRECT=http://localhost:3000

# Optional extras used by app/config.py
ENV=development
API_KEY=
```

4) Run the server

```bash
# Option A: via helper script
./run.sh

# Option B: directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the docs: `http://localhost:8000/docs`.

---

### Project Structure

```text
backend/
  app/
    main.py                # App factory, middleware, routers
    config.py              # Simple config via environment variables
    routes/
      find_song.py         # /music endpoints (recognition + samples scraping)
      spotify.py           # /spotify endpoints (OAuth flow, profile)
    schemas/
      music.py             # Pydantic models for responses
    services/
      music_service.py     # Shazam recognition + WhoSampled scraping
  run.sh                   # Dev run script (uvicorn)
  requirements.txt         # Base Python deps
  example_curls.txt        # Handy cURL examples
```

---

### Environment Variables
- **SESSION_SECRET_KEY**: Required for session cookies (any long random string).
- **SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET / SPOTIFY_REDIRECT_URI**: Required for Spotify login.
  - For local dev, `SPOTIFY_REDIRECT_URI` typically: `http://localhost:8000/spotify/callback`.
- **FRONTEND_REDIRECT**: Where to redirect after Spotify auth (default `http://localhost:3000`).
- **ENV, API_KEY**: Optional, available via `app/config.py`.

Add `.env` to the project root (same directory as this README). The repo `.gitignore` already excludes `.env`.

---

### API Reference

Base URL: `http://localhost:8000`

#### Music
- **POST** `/music/`
  - Multipart form upload, field name: `file` (audio/*)
  - Response body (example):
    ```json
    {
      "song": "N.Y. State of Mind",
      "artist": "Nas",
      "img_url": "https://.../cover.jpg"
    }
    ```

- **GET** `/music/scrape-samples/?song_title={title}&artist={artist}`
  - Returns a list of samples found on WhoSampled.
  - Response body (example):
    ```json
    {
      "samples": [
        {
          "song": "Sampled Song",
          "artist": "Sample Artist",
          "year": "1977",
          "element": "Drums",
          "img_url": "https://www.whosampled.com/path/to/img.jpg"
        }
      ]
    }
    ```

Notes:
- Uploaded audio is written temporarily to `/tmp` and deleted after processing.
- Only basic content-type validation is performed (`audio/*`).

#### Spotify
- **GET** `/spotify/login`
  - Redirects to Spotify consent page.

- **GET** `/spotify/callback?code=...`
  - Spotify redirects here. Exchanges `code` for a token and stores it in the session.
  - Redirects user to `FRONTEND_REDIRECT`.

- **GET** `/spotify/check-login`
  - Returns 401 if not authenticated; otherwise `{ "isConnected": true }`.

- **GET** `/spotify/profile`
  - Requires a valid session token (refreshes if expired).
  - Returns Spotify current user top tracks (first 10).

- **GET** `/spotify/logout`
  - Clears session token.

---

### Example Requests (cURL)

Audio recognition:
```bash
curl -X POST \
  -F "file=@rakim.mp3;type=audio/mpeg" \
  http://localhost:8000/music/
```

Scrape samples:
```bash
curl -G "http://localhost:8000/music/scrape-samples/" \
  --data-urlencode "song_title=YourSongTitle" \
  --data-urlencode "artist=YourArtistName"
```

---

### Spotify App Setup (for OAuth)
1) Create a Spotify app at the Spotify Developer Dashboard.
2) Add Redirect URI: `http://localhost:8000/spotify/callback` (must exactly match `SPOTIFY_REDIRECT_URI`).
3) Copy `Client ID` and `Client Secret` to `.env`.
4) Start the backend, hit `/spotify/login` to begin the flow.

---

### Playwright Notes
This project uses Playwright (Python) to scrape WhoSampled:

- Install: `pip install playwright` then `python -m playwright install chromium`.
- The scraper runs headless with a desktop Chrome user-agent. If pages change or additional bot mitigation appears, you may need to adjust selectors in `app/services/music_service.py`.

---

### Troubleshooting
- "Shazam recognition failed" or empty matches
  - Ensure `shazamio` is installed and the audio clip is long enough and clear.
  - Try a different audio format; if issues persist, installing `ffmpeg` may help with conversions.

- Playwright errors (navigation timeouts / selector not found)
  - Run `python -m playwright install chromium`.
  - Verify network access; WhoSampled can change markup—update selectors if needed.

- 401 from Spotify endpoints
  - Ensure `SESSION_SECRET_KEY` is set.
  - Verify Spotify credentials and redirect URI in `.env`.

---

### Development Tips
- CORS is wide open for development in `app/main.py`. Tighten for production.
- OpenAPI docs live at `/docs` and `/redoc`.
- Session data is stored in a signed cookie (Starlette `SessionMiddleware`).

---

### License
Add a license of your choice for distribution and usage.


