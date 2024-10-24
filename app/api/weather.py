from fastapi import APIRouter
from pydantic import BaseModel
import openmeteo_requests
import requests_cache
from retry_requests import retry

router = APIRouter()

from config import Config

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

class CurrentWeatherRequest(BaseModel):
    latitude: float
    longitude: float

class CurrentWeatherResponse(BaseModel):
    time: str
    temperature_2m: float
    rain: float

@router.post('/current_weather/')
async def get_current_weather(weather_request: CurrentWeatherRequest):
    params = {
        "latitude": weather_request.latitude,
        "longitude": weather_request.longitude,
        "current": ["temperature_2m", "rain"]
    }

    try:
        responses = openmeteo.weather_api(Config.API_URL, params=params)
        
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