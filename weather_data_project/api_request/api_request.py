import os
import requests

def fetch_weather(city='New York'):
    print(f"Fetching weather for {city}")
    
    # Get API key from environment
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        raise EnvironmentError("RAPIDAPI_KEY not found in environment variables")
    
    print(f"API key found: {api_key[:10]}..." if len(api_key) > 10 else "API key found")
    
    url = "https://open-weather13.p.rapidapi.com/city"
    querystring = {"city": city, "lang": "EN", "units": "metric"}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "open-weather13.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        if response.status_code != 200:
            print(f"API error: {data.get('message', 'Unknown error')}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {data}")
            return None
        print("API response received successfully")
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    # Test the function when run directly
    city = 'Johannesburg'
    try:
        data = fetch_weather(city)
        if data:
            print(f"Weather data for {city}: {data}")
        else:
            print("Failed to fetch weather data")
    except Exception as e:
        print(f"Error: {e}")