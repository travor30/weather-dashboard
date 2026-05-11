"""
weather_api.py
==============
Reusable functions for fetching weather data from Open-Meteo and
geocoding city names via Nominatim. No API key required.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Showers", 82: "Heavy showers", 95: "Thunderstorm",
    99: "Thunderstorm + hail",
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://api.open-meteo.com/v1/archive"
HEADERS = {"User-Agent": "WeatherDashboard/1.0 (portfolio project)"}


def geocode_city(city: str) -> dict:
    """
    Resolve a city name to coordinates using Nominatim (OpenStreetMap).

    Args:
        city: City name string, e.g. "London" or "New York, US"

    Returns:
        Dict with keys: lat, lon, display_name

    Raises:
        ValueError: If the city is not found
        requests.RequestException: On network errors
    """
    params = {"q": city, "format": "json", "limit": 1}
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"City '{city}' not found.")
    r = results[0]
    return {"lat": float(r["lat"]), "lon": float(r["lon"]), "display_name": r["display_name"]}


def fetch_current(lat: float, lon: float) -> dict:
    """
    Fetch current weather conditions.

    Returns a dict with temperature, humidity, wind speed, condition, etc.
    """
    params = {
        "latitude": lat, "longitude": lon, "timezone": "auto",
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "wind_speed_10m", "wind_direction_10m", "weather_code",
            "precipitation", "surface_pressure",
        ],
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()["current"]
    data["condition"] = WMO_CODES.get(data["weather_code"], "Unknown")
    return data


def fetch_forecast(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    """
    Fetch daily forecast for the next `days` days.

    Returns a DataFrame with columns:
        time, temperature_2m_max, temperature_2m_min,
        precipitation_sum, weather_code, wind_speed_10m_max, condition, day
    """
    params = {
        "latitude": lat, "longitude": lon, "timezone": "auto",
        "forecast_days": days,
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "weather_code", "wind_speed_10m_max",
        ],
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json()["daily"])
    df["time"] = pd.to_datetime(df["time"])
    df["condition"] = df["weather_code"].map(WMO_CODES).fillna("Unknown")
    df["day"] = df["time"].dt.strftime("%a %d %b")
    return df


def fetch_historical(lat: float, lon: float, days: int = 30) -> pd.DataFrame:
    """
    Fetch historical daily weather for the past `days` days.

    Returns a DataFrame with columns:
        time, temperature_2m_max, temperature_2m_min, precipitation_sum
    """
    end = datetime.today() - timedelta(days=1)
    start = end - timedelta(days=days)
    params = {
        "latitude": lat, "longitude": lon, "timezone": "auto",
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    }
    resp = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=10)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json()["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df


if __name__ == "__main__":
    print("Weather API — quick test")
    geo = geocode_city("London")
    print(f"Geocoded: {geo['display_name'][:50]}")
    current = fetch_current(geo["lat"], geo["lon"])
    print(f"Current:  {current['temperature_2m']}°C, {current['condition']}")
    forecast = fetch_forecast(geo["lat"], geo["lon"])
    print(f"Forecast: {len(forecast)} days fetched")
    print(forecast[["day", "temperature_2m_max", "temperature_2m_min", "condition"]].to_string(index=False))
