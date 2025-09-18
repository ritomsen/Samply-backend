from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

router = APIRouter()

# Define the required scope (adjust scopes as needed)
SPOTIFY_SCOPE = "user-read-email user-top-read"

@router.get("/login")
def spotify_login():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SPOTIFY_SCOPE,
        cache_path=".cache-spotify"
    )
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@router.get("/callback")
def spotify_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")
    
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SPOTIFY_SCOPE,
        cache_path=".cache-spotify"
    )
    
    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")
    
    # Store token info in the server-side session
    request.session["token_info"] = token_info
    
    # Redirect the user to your frontend
    frontend_url = os.getenv("FRONTEND_REDIRECT", "http://localhost:3000")
    return RedirectResponse(frontend_url)

@router.get("/check-login")
def check_login(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    

    access_token = token_info.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    
    return {"isConnected": True}

@router.get("/profile")
def get_profile(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    # Check if token is expired
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SPOTIFY_SCOPE,
        cache_path=".cache-spotify"
    )
    
    # If token is expired, try to refresh it
    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            request.session["token_info"] = token_info
        except Exception:
            raise HTTPException(status_code=401, detail="Token expired and refresh failed")
    
    print(token_info)
    
    access_token = token_info.get("access_token")
    print(access_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    
    sp = spotipy.Spotify(auth=access_token)
    try:
        top_tracks = sp.current_user_top_tracks(limit=10)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return top_tracks 

@router.get("/logout")
def logout(request: Request):
    request.session.pop("token_info", None)
    return {"detail": "Logged out successfully"}