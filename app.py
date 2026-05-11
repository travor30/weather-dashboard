"""
Weather API Dashboard
=====================
A live weather dashboard using the Open-Meteo API (no API key required).
Shows current conditions, 7-day forecast, and historical temperature trends.

Run with:
    streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
)

# ── WMO weather condition codes ───────────────────────────────────────────────
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Showers", 82: "Heavy showers", 95: "Thunderstorm",
    99: "Thunderstorm + hail",
}


def geocode_city(city: str) -> dict:
    """Convert a city name to latitude/longitude using Nominatim."""
    url = f"https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": "WeatherDashboard/1.0"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    results = response.json()
    if not results:
        raise ValueError(f"City '{city}' not found. Try a different spelling.")
    r = results[0]
    return {
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "display_name": r["display_name"],
    }


def fetch_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather conditions from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "wind_speed_10m", "wind_direction_10m", "weather_code",
            "precipitation", "surface_pressure",
        ],
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["current"]


def fetch_forecast(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    """Fetch daily forecast data from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "weather_code", "wind_speed_10m_max",
        ],
        "timezone": "auto",
        "forecast_days": days,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    daily = response.json()["daily"]
    df = pd.DataFrame(daily)
    df["time"] = pd.to_datetime(df["time"])
    df["condition"] = df["weather_code"].map(WMO_CODES).fillna("Unknown")
    df["day"] = df["time"].dt.strftime("%a %d %b")
    return df


def fetch_historical(lat: float, lon: float, days: int = 30) -> pd.DataFrame:
    """Fetch historical temperature data from Open-Meteo."""
    end = datetime.today() - timedelta(days=1)
    start = end - timedelta(days=days)
    url = "https://api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    daily = response.json()["daily"]
    df = pd.DataFrame(daily)
    df["time"] = pd.to_datetime(df["time"])
    return df


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🌤️ Weather Dashboard")
st.markdown("Live weather data powered by the **Open-Meteo API** — no API key required.")

col_input, col_btn = st.columns([4, 1])
with col_input:
    city = st.text_input("City", value="London", label_visibility="collapsed", placeholder="Enter a city...")
with col_btn:
    search = st.button("Search", type="primary", use_container_width=True)

quick_cities = ["London", "New York", "Tokyo", "Lagos", "Sydney", "Paris", "Dubai"]
selected = st.pills("Quick select", quick_cities, default=None)
if selected:
    city = selected

if city:
    try:
        with st.spinner(f"Fetching weather for {city}..."):
            geo = geocode_city(city)
            current = fetch_current_weather(geo["lat"], geo["lon"])
            forecast_df = fetch_forecast(geo["lat"], geo["lon"])
            history_df = fetch_historical(geo["lat"], geo["lon"])

        parts = geo["display_name"].split(",")
        city_label = parts[0].strip()
        country = parts[-1].strip()

        st.subheader(f"{city_label}, {country}")
        st.caption(WMO_CODES.get(current["weather_code"], "Unknown conditions"))

        # ── Current conditions ────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("🌡️ Temperature", f"{round(current['temperature_2m'])}°C")
        m2.metric("🤔 Feels like", f"{round(current['apparent_temperature'])}°C")
        m3.metric("💧 Humidity", f"{round(current['relative_humidity_2m'])}%")
        m4.metric("💨 Wind", f"{round(current['wind_speed_10m'])} km/h")
        m5.metric("🌧️ Precipitation", f"{round(current['precipitation'], 1)} mm")

        st.divider()

        # ── 7-day forecast ────────────────────────────────────────────────────
        st.subheader("7-day forecast")

        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["day"], y=forecast_df["temperature_2m_max"],
            name="Max °C", line=dict(color="#D85A30", width=2),
            mode="lines+markers", marker=dict(size=6),
        ))
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df["day"], y=forecast_df["temperature_2m_min"],
            name="Min °C", line=dict(color="#378ADD", width=2, dash="dot"),
            mode="lines+markers", marker=dict(size=6),
        ))
        fig_forecast.update_layout(
            height=280, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=1.1),
            yaxis_title="°C", xaxis_title="",
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Forecast cards
        cols = st.columns(7)
        for i, row in forecast_df.iterrows():
            with cols[i]:
                st.markdown(f"**{row['day'].split()[0]}**")
                st.markdown(f"↑ {round(row['temperature_2m_max'])}°")
                st.markdown(f"↓ {round(row['temperature_2m_min'])}°")
                st.caption(row["condition"][:12])

        st.divider()

        # ── Historical trend ──────────────────────────────────────────────────
        st.subheader("Last 30 days temperature trend")

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=history_df["time"], y=history_df["temperature_2m_max"],
            name="Max °C", fill="tonexty", line=dict(color="#D85A30", width=1.5),
        ))
        fig_hist.add_trace(go.Scatter(
            x=history_df["time"], y=history_df["temperature_2m_min"],
            name="Min °C", fill="tozeroy", line=dict(color="#378ADD", width=1.5),
        ))
        fig_hist.update_layout(
            height=260, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=1.1),
            yaxis_title="°C",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # ── Precipitation bar chart ───────────────────────────────────────────
        st.subheader("Daily precipitation (last 30 days)")
        fig_rain = px.bar(
            history_df, x="time", y="precipitation_sum",
            labels={"time": "", "precipitation_sum": "mm"},
            color_discrete_sequence=["#378ADD"],
        )
        fig_rain.update_layout(height=220, margin=dict(t=10, b=10))
        st.plotly_chart(fig_rain, use_container_width=True)

        # ── Raw data download ─────────────────────────────────────────────────
        with st.expander("Download forecast data"):
            st.dataframe(forecast_df[["day", "temperature_2m_max", "temperature_2m_min",
                                       "precipitation_sum", "condition"]], use_container_width=True)
            csv = forecast_df.to_csv(index=False)
            st.download_button("📥 Download as CSV", csv, f"{city_label}_forecast.csv", "text/csv")

    except ValueError as e:
        st.error(str(e))
    except requests.RequestException:
        st.error("Could not connect to the weather API. Please check your internet connection.")

st.divider()
st.caption("Data: Open-Meteo (weather) · Nominatim/OpenStreetMap (geocoding) · Both free, no API key needed.")
