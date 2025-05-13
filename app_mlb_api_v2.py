
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MLB SmartBet", layout="centered")

st.title("⚾ MLB SmartBet – Mejores Apuestas del Día con API")

api_key = "5e0eaafdf9a676d39685522b7fcd6a3b"  # Clave API válida

# Selección de fecha
fecha = st.date_input("Selecciona una fecha:", value=datetime.today())
fecha_str = fecha.strftime("%Y-%m-%d")

st.markdown("⏳ Consultando partidos en vivo...")

# Llamada a la API
url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=h2h&dateFormat=iso&oddsFormat=decimal&apiKey={api_key}"
response = requests.get(url)

if response.status_code == 200:
    juegos = response.json()
    partidos = []

    for juego in juegos:
        # Fecha y hora del evento
        inicio = juego.get("commence_time", "")
        fecha_evento = inicio.split("T")[0]

        if fecha_evento == fecha_str:
            equipos = juego.get("teams", [])
            home = juego.get("home_team", "")
            bookies = juego.get("bookmakers", [])

            if len(equipos) == 2 and bookies:
                visitante = equipos[0] if equipos[1] == home else equipos[1]

                for casa in bookies:
                    if casa["title"] == "DraftKings":
                        cuotas = casa["markets"][0]["outcomes"]
                        cuota_home = cuota_away = None

                        for c in cuotas:
                            if c["name"] == home:
                                cuota_home = c["price"]
                            elif c["name"] == visitante:
                                cuota_away = c["price"]

                        if cuota_home and cuota_away:
                            partidos.append({
                                "Partido": f"{home} vs {visitante}",
                                "Cuota Local": cuota_home,
                                "Cuota Visitante": cuota_away
                            })

    if partidos:
        df = pd.DataFrame(partidos)
        st.dataframe(df)
    else:
        st.warning("No hay partidos disponibles para esta fecha.")
else:
    st.error("Error al consultar la API. Verifica tu clave o conexión.")
