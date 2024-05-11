import requests
import customtkinter as ctk
import tkinter
import pandas as pd
import matplotlib as mp
import smtplib
import time
import sqlite3

def create_db():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY,
        temp REAL,
        temp_feels_like REAL,
        wind_speed REAL,
        humidade INTEGER,
        quant_nuvens INTEGER
    )
    """)
    conn.commit()
    conn.close()

def insert_data_to_db(data):
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO weather_data (temp, temp_feels_like, wind_speed, humidade, quant_nuvens) VALUES (?, ?, ?, ?, ?)
    """, (data['temp'], data['temp_feels_like'], data['wind_speed'], data['humidade'], data['quant_nuvens']))
    conn.commit()
    conn.close()

def get_data_from_db():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM weather_data
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def print_db():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_data")
    rows = cursor.fetchall()

    for row in rows:
        print(
            f"ID: {row[0]},"
            f" Temperatura: {row[1]} ºC,"
            f" Sensação Térmica: {row[2]} ºC,"
            f" Velocidade do Vento: {row[3]} m/s,"
            f" Humidade: {row[4]},"
            f" Quantidade de Nuvens: {row[5]}")

    conn.close()

def get_weather_data(api_key, cidade, unidade):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    url= base_url + "appid=" + api_key + "&q=" + cidade + "&units=" + unidade

    response = requests.get(url).json()

    weather_data = {}

    if response['cod'] == '404':
        print("Cidade nao encontrada")
    else:
        weather_data['temp'] = response['main']['temp']
        weather_data['temp_feels_like'] = response['main']['feels_like']
        weather_data['wind_speed'] = response['wind']['speed']
        weather_data['humidade'] = response['main']['humidity']
        weather_data['quant_nuvens'] = response['clouds']['all']

    return weather_data
def get_multiple_weather_data(api_key, cidade, unidade, num_requests, interval):
    weather_data_list = []
    for _ in range(num_requests):
        weather_data = get_weather_data(api_key, cidade, unidade)
        weather_data_list.append(weather_data)
        insert_data_to_db(weather_data)
        time.sleep(interval)

    weather_data_df = pd.DataFrame(weather_data_list)

    return weather_data_df

def analyze_weather_data(weather_data_df):
    if weather_data_df.empty:
        print("Nenhum dado de clima disponível para análise.")
        return

    print(f"Análise dos dados do clima:")
    print(f"Temperatura média: {weather_data_df['temp'].mean()} ºC")
    print(f"Sensação térmica média: {weather_data_df['temp_feels_like'].mean()} ºC")
    print(f"Velocidade média do vento: {weather_data_df['wind_speed'].mean()} m/s")
    print(f"Humidade média: {weather_data_df['humidade'].mean()}")
    print(f"Quantidade média de nuvens: {weather_data_df['quant_nuvens'].mean()}")

def checkDisasters(weather_data_df):
    if weather_data_df.empty:
        print("Nenhum dado de clima disponível para análise.")
        return

    # Definir os limites para cada tipo de desastre
    limite_vento_furacao = 33  # m/s

    # Verificar se algum dos limites foi excedido
    if weather_data_df['wind_speed'].mean() > limite_vento_furacao:
        print("Alerta! Condições potenciais de furacão detectadas.")

print_db()


# Exemplo de uso:
# weather_data_df = get_multiple_weather_data(api_key, cidade, unidade, num_requests, interval)
# analyze_weather_data(weather_data_df)


#weather_data_df = get_multiple_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "Vila Real, PT", "metric", 2, 10)
#print(weather_data_df)
#analyze_weather_data(weather_data_df)
#checkDisasters(weather_data_df)



#   "https://api.openweathermap.org/data/2.5/weather?lat=41.295900&lon=-7.746350&appid=8ba62249b68f6b02f4cc69cae7495cb3" para ver Vila Real, PT em JSON

# Latitule Vila Real,PT -> 41.295900 , Longitude Vila Real,PT -> -7.746350















def send_notification_to_email(subject, message, to_email, from_email="your-email@example.com", password="your-password"):
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Log in to the server
    server.login(from_email, password)

    # Create the email
    email_message = f"Subject: {subject}\n\n{message}"

    # Send the email
    server.sendmail(from_email, to_email, email_message)

    # Close the connection to the server
    server.quit()

# Usage
send_notification_to_email("Hello", "This is a test email", "user-email@example.com")





