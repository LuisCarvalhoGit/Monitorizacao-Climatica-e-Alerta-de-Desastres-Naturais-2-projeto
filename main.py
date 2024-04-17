import requests
import customtkinter
import tkinter
import datetime as dt

def get_weather_data(api_key, location):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    params = {"key": api_key, "q": location}

    response = requests.get(base_url, params=params)
    data = response.json()
    return data

