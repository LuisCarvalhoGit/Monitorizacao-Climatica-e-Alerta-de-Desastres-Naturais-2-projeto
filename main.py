import requests
import customtkinter
import tkinter
import pandas as pd
import matplotlib as mp

def get_weather_data(api_key, cidade, unidade):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    url= base_url + "appid=" + api_key + "&q=" + cidade + "&units=" + unidade

    response = requests.get(url).json()

    if response['cod'] == '404':
        print("Cidade nao encontrada")
    else:
        temp = response['main']['temp']
        temp_feels_like = response ['main']['feels_like']
        wind_speed = response['wind']['speed']
        humidade = response['main']['humidity']
        quant_nuvens = response['clouds']['all']
        print(f"Temperatura em {cidade}(ºC): {temp:.2f} ºC")
        print(f"Sensação Termica em {cidade}(ºC): {temp_feels_like:.2f} ºC")
        print(f"Velocidade do Vento em {cidade}: {wind_speed} m/s")
        print(f"Humidade em {cidade}: {humidade}")
        print(f"Quantidade de Nuvens em {cidade}: {quant_nuvens}")



get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "Vila Real,PT", "metric")  # usar com cuidado, existe limite


#   "https://api.openweathermap.org/data/2.5/weather?lat=41.295900&lon=-7.746350&appid=8ba62249b68f6b02f4cc69cae7495cb3" para ver Vila Real, PT em JSON

# Latitule Vila Real,PT -> 41.295900 , Longitude Vila Real,PT -> -7.746350



