
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MLB SmartBet – Mejores Apuestas del Día con API", layout="centered")

st.markdown("## ⚾ MLB SmartBet – Mejores Apuestas del Día con API")

date = st.date_input("Selecciona una fecha:")
st.write("⏳ Consultando partidos en vivo...")

API_KEY = "5e0eaafdf9a676d39685522b7fcd6a3b"
sport = "baseball_mlb"
region = "us"
market = "h2h"

url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions={region}&markets={market}&date={date}&apiKey={API_KEY}"

try:
    response = requests.get(url)
    data = response.json()

    if "message" in data:
        st.error("Error al consultar la API. Verifica tu clave o conexión.")
    elif not data:
        st.warning("No hay partidos disponibles para esta fecha.")
    else:
        rows = []
        for game in data:
            teams = game["teams"]
            home_team = game["home_team"]
            away_team = [t for t in teams if t != home_team][0]
            bookmakers = game.get("bookmakers", [])
            if bookmakers:
                outcomes = bookmakers[0]["markets"][0]["outcomes"]
                home_odds = next((o["price"] for o in outcomes if o["name"] == home_team), None)
                away_odds = next((o["price"] for o in outcomes if o["name"] == away_team), None)
                rows.append({
                    "Partido": f"{home_team} vs {away_team}",
                    "Cuota Local": home_odds,
                    "Cuota Visitante": away_odds
                })

        df = pd.DataFrame(rows)
        st.dataframe(df)

except Exception as e:
    st.error("Ocurrió un error al procesar los datos de la API.")
