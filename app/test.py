import openmeteo_requests
from datetime import datetime, timedelta
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

today = datetime.now()
end_date = today.strftime("%Y-%m-%d")
start_date = today - timedelta(hours=168)
start_date = start_date.strftime("%Y-%m-%d")

params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": start_date,  # Use start_date directly
    "end_date": end_date,      # Use end_date directly
    "hourly": "temperature_2m"
}


# params = {
# 	"latitude": 52.52,
# 	"longitude": 13.41,
#     "start_date": "2024-10-28 14:00:00+00:00",
#     "end_date": "2024-11-04 14:00:00+00:00",
#     "hourly": "temperature_2m"
# }
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

# print(len(hourly_temperature_2m))
# hourly_temperature_2m is arrray of np.float32
# convert to list of float


      

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m

# get only this time and back to 168 hours
current = datetime.now()
# select from dataframe
#                          date  temperature_2m
# 0   2024-10-28 00:00:00+00:00        8.695499
# 1   2024-10-28 01:00:00+00:00        8.245500
# 2   2024-10-28 02:00:00+00:00        7.745500
# 3   2024-10-28 03:00:00+00:00        7.145500
# 4   2024-10-28 04:00:00+00:00        7.395500
# ..                        ...             ...
# 187 2024-11-04 19:00:00+00:00        8.495500
# 188 2024-11-04 20:00:00+00:00        8.345500
# 189 2024-11-04 21:00:00+00:00        8.395500
# 190 2024-11-04 22:00:00+00:00        8.295500
# 191 2024-11-04 23:00:00+00:00        7.895500

# example this time is 2024-11-04 14:30:00+00:00
# need to convert this time to 2024-11-04 14:00:00+00:00
# we need to get data from 2024-10-28 14:00:00+00:00

# convert to dataframe
hourly_dataframe = pd.DataFrame(hourly_data)

# get only this time and back to 168 hours
# TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and datetime
# example current is 2024-11-04 14:30:00+00:00
# need to convert current to 2024-11-04 14:00:00+00:00

current = datetime.now()
current = current.replace(minute=0, second=0, microsecond=0)
current = pd.to_datetime(current, utc = True)
print(current)
start_time = current - timedelta(hours=167)
print(start_time)

# select from dataframe

hourly_dataframe = hourly_dataframe[(hourly_dataframe['date'] >= start_time) & (hourly_dataframe['date'] <= current)]
print(hourly_dataframe)

# convert hourly_dataframe to list without index

# drop index
# hourly_dataframe = hourly_dataframe.reset_index(drop=True)
# convert to list
hourly_temperature_2m = hourly_dataframe['temperature_2m'].tolist()
print(hourly_temperature_2m)



# print(hourly_dataframe)