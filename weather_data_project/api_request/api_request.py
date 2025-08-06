import requests
import os


def fetch_weather(city, lang="EN"):
    """Get weather data for a city"""
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        raise Exception("RAPIDAPI_KEY environment variable not set")
    
    url = "https://open-weather13.p.rapidapi.com/city"
    
    querystring = {"city": city, "lang": lang}
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "open-weather13.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    return response.json()