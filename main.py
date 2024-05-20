import requests
import customtkinter as ctk

import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import time
import sqlite3
from tabulate import tabulate
from PIL import Image
import re

def celsius_to_fahrenheit(celsius):
    fahrenheit = celsius * (9/5) + 32
    return fahrenheit

def MetersPerSecond_to_KilometersPerHour(MetersPerSecond):
    KilometersPerHour = MetersPerSecond * 3.6
    return KilometersPerHour



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
        weather_data['temp'] = int(response['main']['temp'])

        weather_data['temp_feels_like'] = int(response['main']['feels_like'])
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



    def Recolherdados(event=None):

        nome = entry_nome.get()
        email = entry_email.get()

        cidade = entry_cidade.get()
        temp_unit = temp_unit_var.get()
        wind_speed_unit = wind_speed_unit_var.get()

        def show_time():
            current_time = time.strftime('%H:%M')  # changed from '%H:%M:%S' to '%H:%M'
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

        # If the name and email are in the correct format, clear the error message and continue with the rest of the function
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

        weather_data = get_weather_data("8ba62249b68f6b02f4cc69cae7495cb3", cidade, "metric")


        refresh_button_data = Image.open("images/refresh_icon.png")
        return_button_data = Image.open("images/voltar.png")

        cidade_label = ctk.CTkLabel(master=weather_interface,text=cidade,font=("Roboto Bold",18))
        cidade_label.pack(anchor="center")

        time_label = ctk.CTkLabel(master=weather_interface)
        time_label.place(x=10,y=70)

        ctk.CTkLabel(master=weather_interface,text="Metereologia Atual",font=("Roboto Bold",18)).place(x=10,y=50)

        ctk.CTkLabel(master=weather_interface,text=f"{weather_data['temp']}",font=("Montserrat",63)).place(x=90,y=100)
        ctk.CTkLabel(master=weather_interface,text="ºC",font=("Roboto",25)).place(x=160,y=110)

        refresh_button = ctk.CTkImage(dark_image=refresh_button_data, light_image=refresh_button_data,size=(20,20))
        return_button = ctk.CTkImage(dark_image=return_button_data, light_image=return_button_data,size=(20,20))

        button_retornar = ctk.CTkButton(master=weather_interface,text="",image=return_button, command=root.deiconify,bg_color="#79828c",fg_color="#1f89a1",width=30)
        button_retornar.place(x=10, y=10)

        button_refresh_page = ctk.CTkButton(master=weather_interface,text="",image=refresh_button,bg_color="#79828c",fg_color="#1f89a1",width=30)
        button_refresh_page.place(x=550,y=10)

        label_vento = ctk.CTkLabel(master=weather_interface,text="Vento",font=("Roboto Bold",14))
        label_vento.place(x=20,y=200)

        label_humidade = ctk.CTkLabel(master=weather_interface,text="Humidade",font=("Roboto Bold",14))
        label_humidade.place(x=100,y=200)

        label_pressao = ctk.CTkLabel(master=weather_interface, text="Pressão", font=("Roboto Bold", 14))
        label_pressao.place(x=210, y=200)

        label_sensacao_termica = ctk.CTkLabel(master=weather_interface, text="Sensação térmica", font=("Roboto", 14))
        label_sensacao_termica.place(x=220,y=138)

        label_quant_nuvens = ctk.CTkLabel(master=weather_interface, text="Quantidade de Nuvens", font=("Roboto Bold", 14))
        label_quant_nuvens.place(x=320,y=200)

        #ctk.CTkLabel(master=weather_interface,text=f"Nome: {nome}\nEmail: {email}\nTemperatura:{temp_unit}\nVento:{wind_speed_unit}",bg_color="#297CAA").pack(padx=10,pady=10)

        sun_image = ctk.CTkLabel(master=weather_interface, text="",image=ctk.CTkImage(dark_image=clouds_and_sun_image_data,light_image=clouds_and_sun_image_data,size=(65,65)))
        sun_image.place(x=15,y=100)

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
    #root.update()
    #entry_nome.focus_set()  # foca o cursor em "Nome" ao abrir
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



criar_interface()






