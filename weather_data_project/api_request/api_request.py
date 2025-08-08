import requests
import os

def get_current_weather(lat=None, lon=None, units="metric", lang="en"):
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        raise Exception("RAPIDAPI_KEY environment variable not set")
    
    if lat is None:
        lat = os.getenv('WEATHER_LAT', '-26.204444')  # Johannesburg lat
    if lon is None:
        lon = os.getenv('WEATHER_LON', '28.045556')   # Johannesburg lon
    
    url = os.getenv('API_URL')
    if not url:
        raise Exception("API_URL environment variable not set")
    
    querystring = {"lat": lat, "lon": lon, "units": units, "lang": lang}
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "weatherbit-v1-mashape.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Weather API request failed: {e}")