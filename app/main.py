from fastapi import FastAPI
from app.routes import find_song
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Music Backend API", version="0.1.0")
    
    # Include music routes
    app.include_router(find_song.router, prefix="/music", tags=["Music"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = create_app()