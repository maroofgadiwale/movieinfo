# Movies API:
import requests
import os

API_KEY = os.environ.get("api_key")
def movie_details(title):
    params = {
        "t": title,
        "plot": "full",
        "apikey": API_KEY,
    }
    response = requests.get(url="https://www.omdbapi.com", params=params)
    data = response.json()
    return data