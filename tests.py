"""
Tests for weather_api.py
Run with: python -m pytest tests.py -v

Note: These tests hit live APIs. Run with --co to collect only, or
mock the requests for offline testing.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from weather_api import geocode_city, fetch_current, fetch_forecast, fetch_historical, WMO_CODES


MOCK_GEO = [{"lat": "51.5074", "lon": "-0.1278", "display_name": "London, England, United Kingdom"}]

MOCK_CURRENT = {
    "current": {
        "temperature_2m": 15.2,
        "relative_humidity_2m": 72,
        "apparent_temperature": 13.8,
        "wind_speed_10m": 18.5,
        "wind_direction_10m": 220,
        "weather_code": 3,
        "precipitation": 0.0,
        "surface_pressure": 1012.0,
    }
}

MOCK_FORECAST = {
    "daily": {
        "time": ["2025-01-01", "2025-01-02", "2025-01-03",
                 "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
        "temperature_2m_max": [12, 14, 11, 13, 15, 10, 9],
        "temperature_2m_min": [6, 7, 5, 8, 9, 4, 3],
        "precipitation_sum": [0.0, 2.1, 0.5, 0.0, 0.0, 3.2, 1.0],
        "weather_code": [1, 61, 3, 0, 2, 63, 55],
        "wind_speed_10m_max": [20, 35, 15, 10, 18, 40, 25],
    }
}

MOCK_HISTORICAL = {
    "daily": {
        "time": ["2024-12-01", "2024-12-02", "2024-12-03"],
        "temperature_2m_max": [10, 12, 8],
        "temperature_2m_min": [4, 5, 2],
        "precipitation_sum": [0.0, 1.5, 3.0],
    }
}


class TestWmoCodes:
    def test_clear_sky_mapped(self):
        assert WMO_CODES[0] == "Clear sky"

    def test_thunderstorm_mapped(self):
        assert WMO_CODES[95] == "Thunderstorm"

    def test_all_values_are_strings(self):
        for v in WMO_CODES.values():
            assert isinstance(v, str)


class TestGeocodeCity:
    @patch("weather_api.requests.get")
    def test_returns_lat_lon(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_GEO, raise_for_status=lambda: None)
        result = geocode_city("London")
        assert result["lat"] == 51.5074
        assert result["lon"] == -0.1278

    @patch("weather_api.requests.get")
    def test_city_not_found_raises(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: [], raise_for_status=lambda: None)
        with pytest.raises(ValueError, match="not found"):
            geocode_city("xyznotacity123")

    @patch("weather_api.requests.get")
    def test_display_name_returned(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_GEO, raise_for_status=lambda: None)
        result = geocode_city("London")
        assert "London" in result["display_name"]


class TestFetchCurrent:
    @patch("weather_api.requests.get")
    def test_returns_temperature(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_CURRENT, raise_for_status=lambda: None)
        result = fetch_current(51.5, -0.1)
        assert result["temperature_2m"] == 15.2

    @patch("weather_api.requests.get")
    def test_condition_added(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_CURRENT, raise_for_status=lambda: None)
        result = fetch_current(51.5, -0.1)
        assert result["condition"] == "Overcast"

    @patch("weather_api.requests.get")
    def test_all_expected_keys_present(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_CURRENT, raise_for_status=lambda: None)
        result = fetch_current(51.5, -0.1)
        for key in ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "condition"]:
            assert key in result


class TestFetchForecast:
    @patch("weather_api.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_FORECAST, raise_for_status=lambda: None)
        df = fetch_forecast(51.5, -0.1)
        assert isinstance(df, pd.DataFrame)

    @patch("weather_api.requests.get")
    def test_has_7_rows(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_FORECAST, raise_for_status=lambda: None)
        df = fetch_forecast(51.5, -0.1)
        assert len(df) == 7

    @patch("weather_api.requests.get")
    def test_condition_column_added(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_FORECAST, raise_for_status=lambda: None)
        df = fetch_forecast(51.5, -0.1)
        assert "condition" in df.columns

    @patch("weather_api.requests.get")
    def test_day_column_added(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_FORECAST, raise_for_status=lambda: None)
        df = fetch_forecast(51.5, -0.1)
        assert "day" in df.columns


class TestFetchHistorical:
    @patch("weather_api.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_HISTORICAL, raise_for_status=lambda: None)
        df = fetch_historical(51.5, -0.1, days=3)
        assert isinstance(df, pd.DataFrame)

    @patch("weather_api.requests.get")
    def test_time_column_is_datetime(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: MOCK_HISTORICAL, raise_for_status=lambda: None)
        df = fetch_historical(51.5, -0.1, days=3)
        assert pd.api.types.is_datetime64_any_dtype(df["time"])
