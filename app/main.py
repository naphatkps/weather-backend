from fastapi import FastAPI
from app.models.base import Base
from app.database import engine
from app.api import user, weather

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(weather.router)