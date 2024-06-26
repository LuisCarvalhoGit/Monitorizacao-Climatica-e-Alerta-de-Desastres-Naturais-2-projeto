import requests
import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import time
import threading
from datetime import datetime
import sqlite3
from tabulate import tabulate
from PIL import Image
import re
import seaborn as sns

# Conversion functions
def Celsius_to_Fahrenheit(celsius):
    """
        Convert temperature from Celsius to Fahrenheit.
    """
    return celsius * (9/5) + 32

def MetersPerSecond_to_KilometersPerHour(MetersPerSecond):
    """
        Convert speed from Meters per Second to Kilometers per Hour.

    """
    return MetersPerSecond * 3.6


# Database functions
def create_db():
    """
        Create the weather_data database table if it does not exist.
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY,
        timestamp TIMESTAMP,
        temp REAL,
        temp_feels_like REAL,
        wind_speed REAL,
        humidade INTEGER,
        quant_nuvens INTEGER,
        pressao INTEGER,
        descricao TEXT,
        cidade TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_data_to_db(data):
    """
        Insert a new record into the weather_data table.
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO weather_data (timestamp, temp, temp_feels_like, wind_speed, humidade, quant_nuvens, pressao, descricao, cidade) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['timestamp'],data['temp'], data['temp_feels_like'], data['wind_speed'], data['humidade'], data['quant_nuvens'],data['pressao'], data['descricao'], data['cidade']))
    conn.commit()
    conn.close()

def insert_dataframe_into_db(data):
    """
        Insert multiple records from a DataFrame into the weather_data table.
    """
    try:
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()

        # Iterate over the rows of the DataFrame
        for index, row in data.iterrows():
            # Insert each row into the weather_data table
            cursor.execute("""
                INSERT INTO weather_data (timestamp, temp, temp_feels_like, wind_speed, humidade, quant_nuvens, pressao, descricao, cidade) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (row['timestamp'],row['temp'], row['temp_feels_like'], row['wind_speed'], row['humidade'], row['quant_nuvens'], row['pressao'],row['descricao'], row['cidade']))

        conn.commit()
        conn.close()

        print("DataFrame inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting DataFrame: {e}")
def get_data_from_db():
    """
        Retrieve all records from the weather_data table.
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM weather_data
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_dataframe_from_db():
    """
        Retrieve all records from the weather_data table as a DataFrame.
    """
    try:
        conn = sqlite3.connect('weather_data.db')
        query = "SELECT * FROM weather_data"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Error reading data from database: {e}")

def delete_row(row_id):
    """
        Delete a specific record from the weather_data table by row ID.
    """
    try:
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weather_data WHERE id=?", (row_id,))
        conn.commit()
        conn.close()

        print(f"Row ID={row_id} deleted successfallay.")
    except sqlite3.Error as e:
        print(f"Error deleting row: {e}")

def delete_all_rows():
    """
        Delete all records from the weather_data table.
    """
    try:
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()

        # Delete all rows from the weather_data table
        cursor.execute("DELETE FROM weather_data")

        conn.commit()
        conn.close()

        print("All rows deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting rows: {e}")

def print_db():
    """
        Print all records from the weather_data table in a tabulated format.
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_data")
    rows = cursor.fetchall()

    headers = ["ID","Tempo(data/hora)", "Temperatura (ºC)", "Sensação Térmica (ºC)", "Velocidade do Vento (m/s)", "Humidade",
               "Quantidade de Nuvens","Pressão","Descrição","Cidade"]
    table = tabulate(rows, headers=headers, tablefmt="pretty")
    print(table)

    conn.close()


# Weather data functions
def get_weather_data(api_key, cidade, unidade):
    """
        Fetch weather data from OpenWeatherMap API for a given city.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    url = base_url + "appid=" + api_key + "&q=" + cidade + "&units=" + unidade

    response = requests.get(url).json()


    if response['cod'] != 200:
        return None

    weather_data = {
        'temp': int(response['main']['temp']),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'temp_feels_like': round(response['main']['feels_like']),
        'wind_speed': response['wind']['speed'],
        'humidade': response['main']['humidity'],
        'quant_nuvens': response['clouds']['all'],
        'pressao': response['main']['pressure'],
        'descricao': response['weather'][0]['main'],
        'cidade': cidade
    }


    return weather_data

def store_weather_data(cidade):
    """
        Collects and stores weather data for the specified city in a SQLite database.
    """
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    while True:

        data = get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", cidade, "metric")
        c.execute("INSERT INTO weather_data (timestamp, temp, temp_feels_like, wind_speed, humidade, quant_nuvens, pressao, descricao, cidade) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (data['timestamp'],data['temp'], data['temp_feels_like'], data['wind_speed'], data['humidade'], data['quant_nuvens'],data['pressao'], data['descricao'], data['cidade']))
        conn.commit()
        time.sleep(60)  # Colects data every 60 seconds

def start_data_collection(cidade):
    """
        Starts a background thread to collect and store weather data for the specified city.
    """
    thread = threading.Thread(target=store_weather_data,args=(cidade,), daemon=True)
    thread.start()


# Analysis and alert functions
def calculate_rate_of_change(weather_data_df, column_name):
    """
    Calculate the rate of change for a given column in the DataFrame.

    Parameters:
    weather_data_df (pd.DataFrame): A DataFrame containing weather data.
    column_name (str): The name of the column for which to calculate the rate of change.

    Returns:
    pd.Series: A series containing the rate of change for the specified column.
    """
    if column_name not in weather_data_df.columns:
        raise ValueError(f"Column {column_name} does not exist in the DataFrame")

    return weather_data_df[column_name].diff().fillna(0)

def analyze_weather_trends(weather_data_df):
    """
    Analyze weather data over time to identify significant trends and rates of change.

    Parameters:
    weather_data_df (pd.DataFrame): A DataFrame containing weather data with the following columns:
        - 'timestamp' (datetime): Timestamp of the data point.
        - 'wind_speed' (float): Wind speed in m/s.
        - 'temp' (float): Temperature in degrees Celsius.
        - 'humidade' (float): Humidity percentage.
        - 'pressao' (float): Atmospheric pressure in hPa.

    Returns:
    dict: A dictionary containing the trends and rates of change for key weather variables.
    """

    if weather_data_df.empty:
        return {
            'max_wind_speed_change': 0,
            'max_temp_change': 0,
            'max_humidity_change': 0,
            'max_pressure_change': 0
        }

    # Ensure the DataFrame is sorted by timestamp
    weather_data_df = weather_data_df.sort_values(by='timestamp')

    # Calculate rates of change for key variables
    wind_speed_change = calculate_rate_of_change(weather_data_df, 'wind_speed')
    temp_change = calculate_rate_of_change(weather_data_df, 'temp')
    humidity_change = calculate_rate_of_change(weather_data_df, 'humidade')
    pressure_change = calculate_rate_of_change(weather_data_df, 'pressao')

    # Identify significant trends or sudden changes
    significant_wind_change = wind_speed_change.abs().max()
    significant_temp_change = temp_change.abs().max()
    significant_humidity_change = humidity_change.abs().max()
    significant_pressure_change = pressure_change.abs().max()

    return {
        'max_wind_speed_change': significant_wind_change,
        'max_temp_change': significant_temp_change,
        'max_humidity_change': significant_humidity_change,
        'max_pressure_change': significant_pressure_change
    }

def checkDisasters(weather_data_df):
    """
    Check weather data for potential disaster conditions.

    Parameters:
    weather_data_df (pd.DataFrame): A DataFrame containing weather data with the following columns:
        - 'timestamp' (datetime): Timestamp of the data point.
        - 'wind_speed' (float): Wind speed in m/s.
        - 'temp' (float): Temperature in degrees Celsius.
        - 'humidity' (float): Humidity percentage.
        - 'pressure' (float): Atmospheric pressure in hPa.

    Returns:
    dict: A dictionary containing the probabilities of various disasters and trends.
        - 'storm_probability': Probability of a storm (%).
        - 'tornado_probability': Probability of a tornado (%).
        - 'hurricane_probability': Probability of a hurricane (%).
        - 'trends': Trends and rates of change for key weather variables.
    """
    if weather_data_df.empty:
        print("Nenhum dado de clima disponível para análise.")
        return {
            'storm_probability': 0,
            'tornado_probability': 0,
            'hurricane_probability': 0,
            'trends': {}
        }

    # Define thresholds
    HURRICANE_WIND_THRESHOLD = 33  # m/s

    # Initialize probability scores
    storm_score = 0
    tornado_score = 0
    hurricane_score = 0

    # Calculate mean values
    temp_mean = weather_data_df['temp'].mean()
    humidity_mean = weather_data_df['humidade'].mean()
    pressure_mean = weather_data_df['pressao'].mean()
    wind_speed_mean = weather_data_df['wind_speed'].mean()

    # Calculate storm probability
    if temp_mean > 30 or temp_mean < 5:
        storm_score += 2
    if humidity_mean > 80:
        storm_score += 2
    if pressure_mean < 1000:
        storm_score += 2
    if wind_speed_mean > 15:
        storm_score += 2

    storm_probability = min((storm_score / 8) * 100, 100)



    # Calculate tornado probability if there is a chance of a storm
    if storm_probability > 20:
        if 20 <= temp_mean <= 30:
            tornado_score += 2
        if pressure_mean < 1000:
            tornado_score += 2
        if humidity_mean > 70:
            tornado_score += 2
        if wind_speed_mean > 20:
            tornado_score += 2

        tornado_probability = min((tornado_score / 8) * 100, 100)
    else:
        tornado_probability = 0

    # Calculate hurricane probability
    if wind_speed_mean > HURRICANE_WIND_THRESHOLD:
        hurricane_score += 3

    if pressure_mean < 990:
        hurricane_score += 3
    if pressure_mean < 990:
        hurricane_score += 2
    if humidity_mean > 85:
        hurricane_score += 1

    hurricane_probability = min((hurricane_score / 6) * 100, 100)

    hurricane_probability = min(hurricane_probability, 5)

    # Analyze weather trends
    trends = analyze_weather_trends(weather_data_df)

    return {
        'storm_probability': storm_probability,
        'tornado_probability': tornado_probability,
        'hurricane_probability': hurricane_probability,
        'trends': trends
    }


def plot_data(cidade):
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()
    # Query database data filtered by city
    c.execute("SELECT * FROM weather_data WHERE cidade = ?", (cidade,))
    rows = c.fetchall()
    conn.commit()

    # Extracts data for plotting
    timestamps = [datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') for row in rows]
    temperatures = [row[2] for row in rows]
    humidities = [row[5] for row in rows]
    pressures = [row[7] for row in rows]

    # Create figures for plotting
    plt.figure(figsize=(7, 6),num="Gráficos")



    # Plotting the temperature
    plt.subplot(3, 1, 1)
    sns.lineplot(x=timestamps, y=temperatures)
    plt.title(f'Temperature Over Time in {cidade}')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')

    # Plotting the humidity
    plt.subplot(3, 1, 2)
    sns.lineplot(x=timestamps, y=humidities)
    plt.title(f'Humidity Over Time in {cidade}')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')

    # Plotting the pressure
    plt.subplot(3, 1, 3)
    sns.lineplot(x=timestamps, y=pressures)
    plt.title(f'Pressure Over Time in {cidade}')
    plt.xlabel('Timestamp')
    plt.ylabel('Pressure (hPa)')

    # Adjust the layout and display the chart
    plt.tight_layout()
    plt.show()


# Email notification function
def send_notification_to_email(subject, message, to_email, from_email="alertsweather0@gmail.com", passkey="rrol wold diuu dwdx"):
    """
        Send an email notification.
    """
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Log in to the server
    server.login(from_email, passkey)

    # Create the email
    email_message = f"Subject: {subject}\n\n{message}"

    # Send the email
    server.sendmail(from_email, to_email, email_message)

    # Close the connection to the server
    server.quit()


# Interface
def criar_interface():
    """
        Create the user interface for collecting weather data and displaying it.
    """


    def Recolherdados(event=None):

        nome = entry_nome.get()
        email = entry_email.get()

        cidade = entry_cidade.get()
        temp_unit = temp_unit_var.get()
        wind_speed_unit = wind_speed_unit_var.get()

        def return_mainscreen():
            weather_interface.destroy()
            root.deiconify()
        def show_time():
            current_time = time.strftime('%H:%M')
            time_label.configure(text=current_time)


        # Check if the name is in the correct format (only letters and spaces)
        if not re.match("^[a-zA-Z ]+$", nome):
            error_message_label.configure(text="")
            error_message_label.configure(text="Nome inválido.\nPor favor insira apenas letras e espaços.")
            return

        # Check if the email is in the correct format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message_label.configure(text="")
            error_message_label.configure(text="Email inválido.\nPor favor insira um formato de email válido.")
            return


        # Check if the city field is empty
        if not cidade:
            error_message_label.configure(text="")
            error_message_label.configure(text="Por favor insira uma cidade.")
            return

        # Fetch weather data
        weather_data = get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", cidade, "metric")

        if not weather_data :
            error_message_label.configure(text="")
            error_message_label.configure(text="Cidade não encontrada.\nPor favor insira um local válido.")
            return

        # If the name and email are in the correct format, and the city is valid, clear the error message and continue with the rest of the function
        error_message_label.configure(text="")

        root.iconify()

        weather_interface = ctk.CTkToplevel()
        weather_interface.geometry("600x400")
        weather_interface.resizable(False, False)
        weather_interface.title("Metereologia")
        weather_interface.configure(fg_color="#297CAA")


        sun_image_data = Image.open("images/sun.png")
        clouds_and_sun_image_data = Image.open("images/clouds_and_sun.png")
        clouds_image_data = Image.open("images/clouds.png")
        rain_image_data = Image.open("images/rain.png")
        storm_image_data = Image.open("images/storm.png")
        snow_image_data = Image.open("images/snow.png")
        fog_image_data = Image.open("images/mist.png")
        smoke_image_data = Image.open("images/smoke.png")
        dust_image_data = Image.open("images/dust.png")
        ash_image_data = Image.open("images/ash.png")
        tornado_image_data = Image.open("images/tornado.png")



        if temp_unit == "F":
            weather_data['temp'] = round(Celsius_to_Fahrenheit(weather_data['temp']))
            weather_data['temp_feels_like'] = round(Celsius_to_Fahrenheit(weather_data['temp_feels_like']))

        if wind_speed_unit == "km/h":
            weather_data['wind_speed'] = round(MetersPerSecond_to_KilometersPerHour(weather_data['wind_speed']),1)

        # Create a DataFrame from weather data for disaster analysis
        weather_data_df = pd.DataFrame([{
            'timestamp': pd.Timestamp.now(),
            'wind_speed': weather_data['wind_speed'],
            'temp': weather_data['temp'],
            'humidade': weather_data['humidade'],
            'pressao': weather_data['pressao']
        }])

        # Check for disasters
        disaster_info = checkDisasters(weather_data_df)

        # Send email notifications if necessary
        if disaster_info['storm_probability'] > 50:
            send_notification_to_email("Storm Alert",
                                        f"A storm is likely in {cidade}. Please take precautions.", email)
        if disaster_info['tornado_probability'] > 30:
            send_notification_to_email("Tornado Alert",
                                        f"A tornado is likely in {cidade}. Please take precautions.", email)
        if disaster_info['hurricane_probability'] > 20:
            send_notification_to_email("Hurricane Alert",
                                        f"A hurricane is likely in {cidade}. Please take precautions.", email)

        def update_weather_image():
            # Mapping weather descriptions to image data
            weather_images = {
                "Thunderstorm": storm_image_data,
                "Clouds": clouds_and_sun_image_data,
                "Rain": rain_image_data,
                "Drizzle": rain_image_data,
                "Snow": snow_image_data,
                "Mist": fog_image_data,
                "Smoke": smoke_image_data,
                "Haze": fog_image_data,
                "Dust": dust_image_data,
                "Fog": fog_image_data,
                "Sand": dust_image_data,
                "Ash": ash_image_data,
                "Squall": storm_image_data,
                "Tornado": tornado_image_data,
                "Clear": sun_image_data,
            }

            # Get the image data based on the weather description, default to clouds_image_data if not found
            image_data = weather_images.get(weather_data['descricao'], clouds_image_data)

            # Update the weather image
            weather_image.configure(image=ctk.CTkImage(dark_image=image_data, light_image=image_data, size=(65, 65)))

        def refresh_weather():
            cidade = entry_cidade.get()
            weather_data = get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", cidade, "metric")

            if temp_unit == "F":
                weather_data['temp'] = round(Celsius_to_Fahrenheit(weather_data['temp']))
                weather_data['temp_feels_like'] = round(Celsius_to_Fahrenheit(weather_data['temp_feels_like']))

            if wind_speed_unit == "km/h":
                weather_data['wind_speed'] = round(MetersPerSecond_to_KilometersPerHour(weather_data['wind_speed']), 1)

            # Update temperature
            temp_label.configure(text=f"{weather_data['temp']}")

            # Update feels-like temperature
            label_sensacao_termica_dados.configure(text=f"{weather_data['temp_feels_like']}")

            # Update wind speed
            if wind_speed_unit == "m/s":
                label_vento_dados.configure(text=f"{weather_data['wind_speed']} m/s")
            else:
                label_vento_dados.configure(text=f"{weather_data['wind_speed']} km/h")

            # Update cloud quantity
            label_quant_nuvens_dados.configure(text=f"{weather_data['quant_nuvens']}")

            # Update pressure
            label_pressao_dados.configure(text=f"{weather_data['pressao']} hPa")

            # Update humidity
            label_humidade_dados.configure(text=f"{weather_data['humidade']} %")

            # Update weather icon
            update_weather_image()

            # Update time
            show_time()


        refresh_button_data = Image.open("images/refresh_icon.png")
        return_button_data = Image.open("images/voltar.png")
        graph_button_data = Image.open("images/graph_icon.png")

        cidade_label = ctk.CTkLabel(master=weather_interface,text=cidade,font=("Roboto Bold",18))
        cidade_label.pack(anchor="center",pady=10)

        time_label = ctk.CTkLabel(master=weather_interface)
        time_label.place(x=10,y=70)

        ctk.CTkLabel(master=weather_interface,text="Metereologia Atual",font=("Roboto Bold",18)).place(x=10,y=50)

        temp_label = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['temp']}",font=("Montserrat",63))
        temp_label.place(x=90,y=100)

        if temp_unit == "ºC":
            unit_temp = ctk.CTkLabel(master=weather_interface,text="ºC",font=("Roboto",25))
            unit_temp.place(x=160,y=110)
        else:
            unit_temp = ctk.CTkLabel(master=weather_interface, text="F", font=("Roboto", 25))
            unit_temp.place(x=160, y=110)

        refresh_button = ctk.CTkImage(dark_image=refresh_button_data, light_image=refresh_button_data,size=(20,20))
        return_button = ctk.CTkImage(dark_image=return_button_data, light_image=return_button_data,size=(20,20))
        graph_button = ctk.CTkImage(dark_image=graph_button_data, light_image=graph_button_data, size=(20, 20))

        button_retornar = ctk.CTkButton(master=weather_interface,text="",image=return_button, command=return_mainscreen,bg_color="#297CAA",fg_color="#1f89a1",width=30)
        button_retornar.place(x=10, y=10)

        button_refresh_page = ctk.CTkButton(master=weather_interface,text="",image=refresh_button,command=refresh_weather,bg_color="#297CAA",fg_color="#1f89a1",width=30)
        button_refresh_page.place(x=550,y=10)

        button_graph = ctk.CTkButton(master=weather_interface, text="", command=lambda: plot_data(cidade), image=graph_button, bg_color="#297CAA", fg_color="#1f89a1", width=30)
        button_graph.place(x=50, y=10)

        label_vento = ctk.CTkLabel(master=weather_interface,text="Vento",font=("Roboto Bold",16))
        label_vento.place(x=20,y=200)

        if wind_speed_unit == "m/s":
            label_vento_dados = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['wind_speed']} m/s",font=("Roboto",14))
            label_vento_dados.place(x=20,y=220)
        else:
            label_vento_dados = ctk.CTkLabel(master=weather_interface, text=f"{weather_data['wind_speed']} km/h", font=("Roboto", 14))
            label_vento_dados.place(x=20, y=220)

        label_humidade = ctk.CTkLabel(master=weather_interface,text="Humidade",font=("Roboto Bold",16))
        label_humidade.place(x=100,y=200)

        label_humidade_dados = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['humidade']} %",font=("Roboto",14))
        label_humidade_dados.place(x=100,y=220)

        label_pressao = ctk.CTkLabel(master=weather_interface, text="Pressão", font=("Roboto Bold", 16))
        label_pressao.place(x=210, y=200)

        label_pressao_dados = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['pressao']} hPa",font=("Roboto",14))
        label_pressao_dados.place(x=210,y=220)

        label_sensacao_termica = ctk.CTkLabel(master=weather_interface, text="Sensação térmica", font=("Roboto", 14))
        label_sensacao_termica.place(x=220,y=138)

        label_sensacao_termica_dados = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['temp_feels_like']}",font=("Montserrat",22))
        label_sensacao_termica_dados.place(x=340,y=138)

        if temp_unit == "ºC":
            ctk.CTkLabel(master=weather_interface, text="ºC",font=("Montserrat", 15)).place(x=368, y=138)
        else:
            ctk.CTkLabel(master=weather_interface, text="F", font=("Montserrat", 15)).place(x=365, y=138)


        label_quant_nuvens = ctk.CTkLabel(master=weather_interface, text="Quantidade de Nuvens", font=("Roboto Bold", 16))
        label_quant_nuvens.place(x=320,y=200)

        label_quant_nuvens_dados = ctk.CTkLabel(master=weather_interface,text=f"{weather_data['quant_nuvens']}",font=("Roboto",14))
        label_quant_nuvens_dados.place(x=320,y=220)

        label_nome = ctk.CTkLabel(master=weather_interface,text=f"Nome do usuário: {nome}", font=("Roboto Bold", 16))
        label_nome.place(x=20,y=320)

        label_email = ctk.CTkLabel(master=weather_interface,text=f"Email do usuário: {email}", font=("Roboto Bold", 16))
        label_email.place(x=20,y=340)

        weather_image = ctk.CTkLabel(master=weather_interface, text="",image=ctk.CTkImage(dark_image=clouds_and_sun_image_data,light_image=clouds_and_sun_image_data,size=(65,65)))
        weather_image.place(x=15,y=100)

        update_weather_image()

        start_data_collection(cidade)

        show_time()

        weather_interface.mainloop()




    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.geometry("600x400")
    root.resizable(False, False)
    root.title("Formulário de Dados do Utilizador")

    # Create option menu widgets for the temperature and wind speed units
    temp_unit_options = ["ºC", "F"]
    wind_speed_unit_options = ["m/s", "km/h"]

    temp_unit_var = ctk.StringVar(value=temp_unit_options[0])  # default value
    wind_speed_unit_var = ctk.StringVar(value=wind_speed_unit_options[0])  # default value


    side_img_data = Image.open("images/side-img.png")

    side_img = ctk.CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))


    ctk.CTkLabel(master=root, text="", image=side_img).pack(expand=True, side="left")

    frame = ctk.CTkFrame(master=root, width=300, height=480, fg_color="#dcddde")
    frame.pack_propagate(False)
    frame.pack(expand=True, side="right")


    error_message_label = ctk.CTkLabel(master=frame, text="", text_color="red")
    error_message_label.pack(anchor="w", padx=(25, 0),pady=(20,0))

    ctk_label_nome = ctk.CTkLabel(master=frame, text ="Bem vindo!" ,font=("Roboto Bold",18),text_color="#296aa3", anchor='w', justify='left')
    ctk_label_nome.pack(anchor="w", pady=(20, 5), padx=(25, 0))

    ctk_label_desc = ctk.CTkLabel(master=frame, text="Insira os seus dados e preferências",text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 15))
    ctk_label_desc.pack(anchor="w", padx=(25, 0))

    entry_nome = ctk.CTkEntry(master=frame, placeholder_text="O seu nome", width=225, placeholder_text_color='#757272',text_color="#303030",fg_color="#EEEEEE",border_color='#757272',border_width=2)
    entry_nome.pack(anchor="w", padx=(25, 0), pady=(10,0))

    entry_email = ctk.CTkEntry(master=frame, placeholder_text="Oseuemail@gmail.com", width=225, placeholder_text_color='#757272',text_color="#303030", fg_color="#EEEEEE", border_color='#757272', border_width=2)
    entry_email.pack(anchor="w", padx=(25, 0), pady=(10,0))

    temp_unit_option_menu = ctk.CTkOptionMenu(master=frame, variable=temp_unit_var, values=temp_unit_options,button_color="#1f89a1",fg_color="#1f89a1",font=("Roboto bold", 15),width=110)
    temp_unit_option_menu.place(y=250,x=25)

    wind_speed_unit_option_menu = ctk.CTkOptionMenu(master=frame, variable=wind_speed_unit_var, values=wind_speed_unit_options, button_color="#1f89a1",fg_color="#1f89a1",font=("Roboto bold", 15),width=110)
    wind_speed_unit_option_menu.place(y=250,x=140)

    entry_cidade = ctk.CTkEntry(master=frame, placeholder_text="Vila Real, PT",width=225,placeholder_text_color='#757272',text_color="#303030", fg_color="#EEEEEE",border_color='#757272', border_width=2)
    entry_cidade.place(x=25,y=215)

    submit_button = ctk.CTkButton(master=frame, text="Submeter", hover_color="#E44982", fg_color="#1f89a1", font=("Roboto bold", 15), width=225, command=Recolherdados)
    submit_button.place(x=25,y=290)



    root.bind('<Return>', Recolherdados)  # bind the Enter key to the Recolherdados function


    root.mainloop()

def main():
    create_db()
    criar_interface()


if __name__ == "__main__":
    main()

