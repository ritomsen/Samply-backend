import os
from dotenv import load_dotenv

# Load environment variables from the .env file early on.
load_dotenv()

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routes import find_song, spotify
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Music Backend API", version="0.1.0")
    
    # Add session middleware. Make sure SESSION_SECRET_KEY is set in the .env file.
    app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
    
    # Include music routes
    app.include_router(find_song.router, prefix="/music", tags=["Music"])
    
    # Include Spotify authentication routes
    app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = create_app()