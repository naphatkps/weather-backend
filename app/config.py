from dotenv import load_dotenv

load_dotenv()

import os

class Config:
    API_URL = os.getenv("API_URL")
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


