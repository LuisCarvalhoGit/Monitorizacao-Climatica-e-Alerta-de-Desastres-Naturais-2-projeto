import requests
import customtkinter as ctk
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import time
import sqlite3
from tabulate import tabulate



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

def insert_dataframe_into_db(data):
    try:
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()

        # Iterate over the rows of the DataFrame
        for index, row in data.iterrows():
            # Insert each row into the weather_data table
            cursor.execute("""
                INSERT INTO weather_data (temp, temp_feels_like, wind_speed, humidade, quant_nuvens) 
                VALUES (?, ?, ?, ?, ?)
            """, (row['temp'], row['temp_feels_like'], row['wind_speed'], row['humidade'], row['quant_nuvens']))

        conn.commit()
        conn.close()

        print("DataFrame inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting DataFrame: {e}")
def get_data_from_db():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM weather_data
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_dataframe_from_db():
    try:
        conn = sqlite3.connect('weather_data.db')
        query = "SELECT * FROM weather_data"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Error reading data from database: {e}")

def delete_row(row_id):
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
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_data")
    rows = cursor.fetchall()

    headers = ["ID", "Temperatura (ºC)", "Sensação Térmica (ºC)", "Velocidade do Vento (m/s)", "Humidade",
               "Quantidade de Nuvens"]
    table = tabulate(rows, headers=headers, tablefmt="pretty")
    print(table)

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

def plot_data():
    # Fetch data from the database
    data = get_data_from_db()

    # Separate the data into different lists
    temp = [row[1] for row in data]
    temp_feels_like = [row[2] for row in data]
    wind_speed = [row[3] for row in data]
    humidade = [row[4] for row in data]
    quant_nuvens = [row[5] for row in data]

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(temp, label='Temperatura')
    plt.plot(temp_feels_like, label='Sensação Térmica')
    plt.plot(wind_speed, label='Velocidade do vento')
    plt.plot(humidade, label='Humidade')
    plt.plot(quant_nuvens, label='Quantidade média de nuvens')
    plt.title('Weather Data over Time')
    plt.xlabel('Tempo')
    plt.ylabel('Valores')
    plt.legend()
    plt.show()

#data_df = get_multiple_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "Vila Real, PT", "metric", 10, 7)
#insert_dataframe_into_db(data_df)




# Exemplo de uso:
# weather_data_df = get_multiple_weather_data(api_key, cidade, unidade, num_requests, interval)
# analyze_weather_data(weather_data_df)


#weather_data_df = get_multiple_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", "Vila Real, PT", "metric", 2, 10)
#print(weather_data_df)
#analyze_weather_data(weather_data_df)
#checkDisasters(weather_data_df)



#   "https://api.openweathermap.org/data/2.5/weather?lat=41.295900&lon=-7.746350&appid=8ba62249b68f6b02f4cc69cae7495cb3" para ver Vila Real, PT em JSON

# Latitule Vila Real,PT -> 41.295900 , Longitude Vila Real,PT -> -7.746350





# rrol wold diuu dwdx = App Password
def send_notification_to_email(subject, message, to_email, from_email="alertsweather0@gmail.com", passkey="rrol wold diuu dwdx"):
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





def criar_interface():
    def Recolherdados():

        nome = entry_nome.get()
        email = entry_email.get()

        weather_interface = ctk.CTk(fg_color='#63a5db')
        weather_interface.geometry("600x400")
        weather_interface.title("Metereologia")
        frame =ctk.CTkFrame(master=weather_interface,fg_color='#dadde0')
        frame.pack(pady=20, padx=60, fill="both", expand=True)
        new_label = ctk.CTkLabel(master=frame, text=f"Nome: {nome}\nEmail: {email}",font=('Roboto',25),text_color='black')
        new_label.pack(pady=20, anchor='w')

        weather_interface.mainloop()



    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.geometry("500x300")
    root.title("Formulário de Dados do Utilizador")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    ctk_label_nome = ctk.CTkLabel(master=frame, text ="Formulário de Entrada" ,font=("Roboto",26))
    ctk_label_nome.pack(pady=12,padx=10)

    entry_nome = ctk.CTkEntry(master=frame, placeholder_text="Nome")
    entry_nome.pack(pady=12,padx=10)


    entry_email = ctk.CTkEntry(master=frame, placeholder_text="Email")
    entry_email.pack(pady=12,padx=10)

    submit_button = ctk.CTkButton(master=frame, text="Submeter", command=Recolherdados)
    submit_button.pack(pady=12,padx=10)

    remember_me_checkbox = ctk.CTkCheckBox(master=frame,text='Lembrar-se de mim',font=('Roboto',15))
    remember_me_checkbox.pack(pady=12,padx=10)

    root.mainloop()

criar_interface()







