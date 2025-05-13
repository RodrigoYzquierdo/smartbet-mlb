
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone

st.set_page_config(page_title="MLB SmartBet API", layout="wide")
st.title("⚾ MLB SmartBet – Mejores Apuestas Futuras con API")
st.markdown("---")

# 🔐 API Key
API_KEY = "5e0eaafdf9a676d39685522b7fcd6a3b"
url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
params = {
    "regions": "us",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "apiKey": API_KEY
}

st.markdown("⌛ Consultando partidos futuros...")
response = requests.get(url, params=params)

if response.status_code != 200:
    st.error("Error al conectar con la API. Verifica tu clave o el límite de uso.")
    st.stop()

datos = response.json()
partidos = []
ahora = datetime.now(timezone.utc)

for evento in datos:
    comienzo = evento.get("commence_time", "")
    try:
        comienzo_dt = datetime.fromisoformat(comienzo.replace("Z", "+00:00"))
        if comienzo_dt >= ahora and "home_team" in evento and "teams" in evento:
            home = evento["home_team"]
            teams = evento["teams"]
            away = next((t for t in teams if t != home), None)
            if away is None:
                continue

            odds_data = evento.get("bookmakers", [])
            if odds_data:
                odds = odds_data[0]["markets"][0]["outcomes"]
                cuotas = {o["name"]: o["price"] for o in odds}
                cuota_local = cuotas.get(home, np.nan)
                cuota_visitante = cuotas.get(away, np.nan)
                partidos.append({
                    "Partido": f"{home} vs {away}",
                    "Fecha": comienzo_dt.strftime("%Y-%m-%d %H:%M"),
                    "Cuota Local": cuota_local,
                    "Cuota Visitante": cuota_visitante,
                    "HomeTeam": home,
                    "AwayTeam": away
                })
    except:
        continue

if not partidos:
    st.warning("No hay partidos disponibles para las próximas horas.")
    st.stop()

df = pd.DataFrame(partidos)

def estimar_probabilidad(cuota):
    return round(1 / cuota if cuota > 0 else 0, 2)

df["Predicción"] = np.where(df["Cuota Local"] < df["Cuota Visitante"], "Local", "Visitante")
df["Probabilidad Estimada"] = np.where(
    df["Predicción"] == "Local",
    df["Cuota Local"].apply(estimar_probabilidad),
    df["Cuota Visitante"].apply(estimar_probabilidad)
)
df["Cuota Elegida"] = np.where(
    df["Predicción"] == "Local",
    df["Cuota Local"],
    df["Cuota Visitante"]
)
df["Value"] = df["Probabilidad Estimada"] * df["Cuota Elegida"]
df["Value Bet"] = np.where(df["Value"] > 1.0, "✅ Sí", "❌ No")

st.markdown("### 🎯 Mejores apuestas de los próximos partidos")
st.dataframe(df[["Fecha", "Partido", "Predicción", "Probabilidad Estimada", "Cuota Elegida", "Value Bet"]], use_container_width=True)

st.markdown("### 💼 Simulación básica")
monto = st.number_input("Monto por apuesta ($)", min_value=10, value=50, step=10)

simulacion = []
ganancia_total = 0
for row in df.itertuples():
    if row.Value > 1.0:
        gana = np.random.rand() < row._7
        ganancia = monto * (row._6 - 1) if gana else -monto
        simulacion.append({
            "Partido": row.Partido,
            "Resultado": "✅ Ganada" if gana else "❌ Perdida",
            "Ganancia": round(ganancia, 2)
        })
        ganancia_total += ganancia

if simulacion:
    st.markdown("### 📈 Resultados de la simulación")
    st.dataframe(pd.DataFrame(simulacion))
    st.success(f"Ganancia neta simulada: ${round(ganancia_total, 2)}")
else:
    st.info("No hay value bets para simular.")
