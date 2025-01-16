from fastapi import FastAPI
from app.routes import find_song

def create_app() -> FastAPI:
    app = FastAPI(title="Music Backend API", version="0.1.0")
    
    # Include music routes
    app.include_router(find_song.router, prefix="/music", tags=["Music"])
    
    return app

app = create_app()