from fastapi import FastAPI
from app.database import db
from app.config import config
from app.api import user, weather
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from app.api.weather import predict_weather,predict

import requests

app = FastAPI()

app.include_router(user.router)
app.include_router(weather.router)

collection = db['users']

def my_daily_task():
    print("This is a daily task that runs every 6 hour")

    response = predict()["predicted_temperatures"]
    # print(type(response))
    avg_temp = sum(response)/len(response)
    # print(avg_temp)
    # print(response)

    users = list(collection.find({}, {"email": 1, "_id": 0}))
    # print(users)
    for user in users:
        # print(user["email"])
        response = requests.post(
            "http://192.168.215.197:8888/noti",
            json={
                "username": "user",
                "email": str(user["email"]),
                "temperature": str(avg_temp)+" C",
            }
        )



scheduler = BackgroundScheduler()
trigger = IntervalTrigger(seconds=3600*6)
scheduler.add_job(my_daily_task, trigger)
scheduler.start()

# app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

