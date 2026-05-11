"""
Weather API Dashboard
=====================
Uses Open-Meteo's own geocoding API to avoid external service blocks.

Run with:
    streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Showers", 82: "Heavy showers", 95: "Thunderstorm", 99: "Thunderstorm + hail",
}

def geocode_city(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        raise ValueError(f"City '{city}' not found.")
    res = data["results"][0]
    return {"lat": res["latitude"], "lon": res["longitude"], "city": res["name"], "country": res.get("country", "")}

def fetch_current(lat, lon):
    params = {"latitude": lat, "longitude": lon, "timezone": "auto",
              "current": ["temperature_2m","relative_humidity_2m","apparent_temperature","wind_speed_10m","weather_code","precipitation"]}
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
    r.raise_for_status()
    return r.json()["current"]

def fetch_forecast(lat, lon):
    params = {"latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 7,
              "daily": ["temperature_2m_max","temperature_2m_min","precipitation_sum","weather_code","wind_speed_10m_max"]}
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["daily"])
    df["time"] = pd.to_datetime(df["time"])
    df["condition"] = df["weather_code"].map(WMO_CODES).fillna("Unknown")
    df["day"] = df["time"].dt.strftime("%a %d %b")
    return df

def fetch_historical(lat, lon):
    end = datetime.today() - timedelta(days=1)
    start = end - timedelta(days=30)
    params = {"latitude": lat, "longitude": lon, "timezone": "auto",
              "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"),
              "daily": ["temperature_2m_max","temperature_2m_min","precipitation_sum"]}
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=10)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df

st.title("🌤️ Weather Dashboard")
st.markdown("Live weather data powered by the **Open-Meteo API** — no API key required.")

col_input, col_btn = st.columns([4, 1])
with col_input:
    city = st.text_input("City", value="London", label_visibility="collapsed")
with col_btn:
    st.button("Search", type="primary", use_container_width=True)

selected = st.pills("Quick select", ["London","New York","Tokyo","Lagos","Sydney","Paris","Dubai"], default=None)
if selected:
    city = selected

if city:
    try:
        with st.spinner(f"Fetching weather for {city}..."):
            geo = geocode_city(city)
            current = fetch_current(geo["lat"], geo["lon"])
            forecast_df = fetch_forecast(geo["lat"], geo["lon"])
            history_df = fetch_historical(geo["lat"], geo["lon"])

        st.subheader(f"{geo['city']}, {geo['country']}")
        st.caption(WMO_CODES.get(current["weather_code"], "Unknown"))

        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("🌡️ Temperature", f"{round(current['temperature_2m'])}°C")
        m2.metric("🤔 Feels like", f"{round(current['apparent_temperature'])}°C")
        m3.metric("💧 Humidity", f"{round(current['relative_humidity_2m'])}%")
        m4.metric("💨 Wind", f"{round(current['wind_speed_10m'])} km/h")
        m5.metric("🌧️ Precipitation", f"{round(current['precipitation'],1)} mm")

        st.divider()
        st.subheader("7-day forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df["day"], y=forecast_df["temperature_2m_max"], name="Max °C", line=dict(color="#D85A30", width=2), mode="lines+markers"))
        fig.add_trace(go.Scatter(x=forecast_df["day"], y=forecast_df["temperature_2m_min"], name="Min °C", line=dict(color="#378ADD", width=2, dash="dot"), mode="lines+markers"))
        fig.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), legend=dict(orientation="h",y=1.1), yaxis_title="°C")
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(7)
        for i, row in forecast_df.iterrows():
            with cols[i]:
                st.markdown(f"**{row['day'].split()[0]}**")
                st.markdown(f"↑ {round(row['temperature_2m_max'])}°")
                st.markdown(f"↓ {round(row['temperature_2m_min'])}°")
                st.caption(row["condition"][:12])

        st.divider()
        st.subheader("Last 30 days")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=history_df["time"], y=history_df["temperature_2m_max"], name="Max °C", fill="tonexty", line=dict(color="#D85A30",width=1.5)))
        fig2.add_trace(go.Scatter(x=history_df["time"], y=history_df["temperature_2m_min"], name="Min °C", fill="tozeroy", line=dict(color="#378ADD",width=1.5)))
        fig2.update_layout(height=260, margin=dict(t=10,b=10,l=10,r=10), legend=dict(orientation="h",y=1.1), yaxis_title="°C")
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander("Download forecast data"):
            csv = forecast_df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, f"{geo['city']}_forecast.csv", "text/csv")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.divider()
st.caption("Data: Open-Meteo API · Free, no API key needed.")
