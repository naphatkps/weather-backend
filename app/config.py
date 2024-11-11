from dotenv import load_dotenv

load_dotenv("./app/.env")

import os

class Config:
    API_URL = os.getenv("API_URL")
    DATABASE_URL = os.getenv("DATABASE_URL")
    GEO_API_KEY = os.getenv("GEO_API_KEY")  

config = Config()