import requests
import os

def fetch_weather(city):
    api_key = os.getenv("RAPIDAPI_KEY")
    api_url = os.getenv("API_URL")

    if not api_key or not api_url:
        raise ValueError("API key or API URL not set")

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_url.replace("https://", "").split("/")[0],
    }

    params = {"q": city}

    print(f"Fetching weather for {city}")
    print(f"API key found: {api_key[:10]}...")

    try:
        response = requests.get(api_url, headers=headers, params=params)
        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error from API: {response.status_code} - {response.text}")
            return None

        if not response.text.strip():
            print("Empty response body.")
            return None

        data = response.json()
        print(f"Weather data for {city}: {data}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    except ValueError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")
        return None
