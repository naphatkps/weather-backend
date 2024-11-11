from fastapi import APIRouter
from pydantic import BaseModel
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
import requests
from app.config import config
import pandas as pd

router = APIRouter()

url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
coordinate_url = "https://api.api-ninjas.com/v1/geocoding"
model_url = "http://localhost:5050/predict"

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# class CurrentWeatherRequest(BaseModel):
#     city: str
#     country: str

class CurrentWeatherResponse(BaseModel):
    time: str
    temperature_2m: float
    rain: float

api = config.GEO_API_KEY

@router.get('/current_weather/')
async def get_current_weather():

    response = requests.get(coordinate_url, 
                            params={"city": "Bangkok", "country": "Thailand"},
                            headers={"x-api-key": api})
    # print(response.json())
    latitude = response.json()[0]["latitude"]
    longitude = response.json()[0]["longitude"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "rain"]
    }

    try:
        responses = openmeteo.weather_api(config.API_URL, params=params)
        
        response = responses[0]

        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_rain = current.Variables(1).Value()

        return {
            "time": current.Time(),
            "temperature_2m": current_temperature_2m,
            "rain": current_rain
        }
    except Exception as e:
        return {"error": str(e)}
    

@router.get('/predict_weather/')
async def predict_weather():
    return predict()

def predict():
    response = requests.get(coordinate_url, 
                            params={"city": "Bangkok", "country": "Thailand"},
                            headers={"x-api-key": api})
    # print(response.json())
    latitude = response.json()[0]["latitude"]
    longitude = response.json()[0]["longitude"]

    today = datetime.now()
    end_date = today.strftime("%Y-%m-%d")
    start_date = today - timedelta(hours=168)
    start_date = start_date.strftime("%Y-%m-%d")

    # print(start_date)
    # print(end_date)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
	    "end_date": end_date,
	    "hourly": "temperature_2m"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_dataframe = pd.DataFrame(hourly_data)
        current = datetime.now()
        current = datetime.now()

        current = current.replace(minute=0, second=0, microsecond=0)
        current = pd.to_datetime(current, utc = True)

        start_time = current - timedelta(hours=167)

        hourly_dataframe = hourly_dataframe[(hourly_dataframe['date'] >= start_time) & (hourly_dataframe['date'] <= current)]

        hourly_temperature_2m = hourly_dataframe['temperature_2m'].tolist()

        # return hourly_temperature_2m
        model_response = requests.post(model_url, json={"temperatures": hourly_temperature_2m})
        # print(model_response)
        return model_response.json()
    
    except Exception as e:
        return {"error": str(e)}
