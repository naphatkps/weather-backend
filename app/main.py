from fastapi import FastAPI
from models.base import Base
from database import engine
from api import user
from api import weather

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(weather.router)