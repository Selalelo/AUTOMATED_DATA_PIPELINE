import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

api_key = os.getenv("RAPIDAPI_KEY")

if not api_key:
    raise EnvironmentError("RAPIDAPI_KEY not found in .env")

def fetch_weather(city='New York'):
    print(f"Fetching weather for {city}")

    url = "https://open-weather13.p.rapidapi.com/city"
    querystring = {"city": city, "lang": "EN", "units":"metric"}
    headers = {
       "x-rapidapi-key": api_key,
       "x-rapidapi-host": "open-weather13.p.rapidapi.com"
     }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        if response.status_code != 200:
            print(f"API error: {data.get('message', 'Unknown error')}")
            return
        print("API response received successfully")
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise



