import requests
import customtkinter
import tkinter
import pandas as pd
import matplotlib as mp
import smtplib

df = pd.DataFrame(columns=['Cidade','Temperatura','Sensação Termica','Velocidade do Vento','Humidade','Quantidade de Nuvens'])

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


        global df
        df = df._append({'Cidade': cidade,
                        'Temperatura': temp,
                        'Sensação Termica': temp_feels_like,
                        'Velocidade do Vento': wind_speed,
                        'Humidade':humidade,
                        'Quantidade de Nuvens':quant_nuvens},
                         ignore_index=True)


get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "Vila Real,PT", "metric")  # usar com cuidado, existe limite

print(df)


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
#   "https://api.openweathermap.org/data/2.5/weather?lat=41.295900&lon=-7.746350&appid=8ba62249b68f6b02f4cc69cae7495cb3" para ver Vila Real, PT em JSON

# Latitule Vila Real,PT -> 41.295900 , Longitude Vila Real,PT -> -7.746350


