import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV: str = os.getenv("ENV", "development")
    API_KEY: str = os.getenv("API_KEY", "")
    # Add other config variables here
