import requests
import customtkinter
import tkinter
import datetime as dt
import pandas as pd

def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius,fahrenheit

def get_weather_data(api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    url= base_url + "appid=" + api_key + "&lat=" + lat + "&lon=" + lon

    response = requests.get(url).json()

    if response['cod'] == '404':
        print("Cidade nao encontrada")
    else:
        temp_kelvin = response["main"]["temp"]
        temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
        print(temp_kelvin)
        print(temp_celsius)



get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "41.295900", "-7.746350")  # usar com cuidado, existe limite


#   "https://api.openweathermap.org/data/2.5/weather?lat=41.295900&lon=-7.746350&appid=8ba62249b68f6b02f4cc69cae7495cb3" para ver Vila Real, PT em JSON

# Latitule Vila Real,PT -> 41.295900 , Longitude Vila Real,PT -> -7.746350



