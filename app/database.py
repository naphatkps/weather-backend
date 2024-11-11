from pymongo import MongoClient
from app.config import config
client = MongoClient(config.DATABASE_URL)
db = client['weather']