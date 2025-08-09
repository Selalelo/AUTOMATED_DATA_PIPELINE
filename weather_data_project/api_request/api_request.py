import os
import requests

def get_current_weather(location: str):
    """
    Fetch current weather data for a given location.
    API credentials and URL are stored in environment variables:
    - API_URL
    - API_KEY
    """
    url = os.getenv("RAPIDAPI_URL")
    api_key = os.getenv("API_KEY")

    if not url or not api_key:
        raise EnvironmentError("API_URL or API_KEY not set in environment variables.")

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "cities-temperature.p.rapidapi.com"
    }
    params = {"location": location}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return None
