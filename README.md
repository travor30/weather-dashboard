# 🌤️ Weather API Dashboard

A live weather dashboard built with Python and Streamlit. Pulls real-time data from the **Open-Meteo API** — completely free, no API key required. Search any city in the world and get current conditions, a 7-day forecast, and 30-day historical trends.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red)
![API](https://img.shields.io/badge/API-Open--Meteo-green)
![Tests](https://img.shields.io/badge/Tests-pytest-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 Features

- **Live current weather** — temperature, feels like, humidity, wind speed, precipitation
- **7-day forecast** — max/min temperature chart + daily condition cards
- **30-day historical trend** — temperature and precipitation charts
- **City search** — search any city worldwide via Nominatim geocoding
- **CSV export** — download forecast data for further analysis
- **No API key needed** — fully free, open data sources

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/weather-dashboard.git
cd weather-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Or test the API module directly
```bash
python weather_api.py
```

---

## 🧪 Running Tests

```bash
python -m pytest tests.py -v
```

Tests use mocked API responses — no internet connection required.

---

## 🏗️ How It Works

```
User enters city name
        ↓
Nominatim API (OpenStreetMap) → geocodes city to lat/lon
        ↓
Open-Meteo API → fetches weather data
        ↓
Pandas → processes data into DataFrames
        ↓
Plotly + Streamlit → renders interactive charts
```

### APIs used

| API | Purpose | Cost |
|-----|---------|------|
| [Open-Meteo](https://open-meteo.com/) | Weather data | Free |
| [Nominatim](https://nominatim.org/) | City → coordinates | Free |

---

## 📁 Project Structure

```
weather-dashboard/
├── app.py              # Streamlit web application
├── weather_api.py      # API wrapper functions (reusable module)
├── tests.py            # Unit tests with mocked APIs
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| Plotly | Interactive charts |
| pandas | Data processing |
| requests | HTTP API calls |
| pytest | Unit testing |
| Open-Meteo | Weather data API |
| Nominatim | Geocoding API |

---

## 🔮 Future Improvements

- [ ] Add hourly forecast view
- [ ] Weather alerts and warnings
- [ ] Compare two cities side by side
- [ ] Unit toggle (°C / °F)
- [ ] Add UV index and air quality data
- [ ] Deploy to Streamlit Cloud (one-click share)

---

## ☁️ Deploy for Free

You can deploy this app publicly on [Streamlit Community Cloud](https://streamlit.io/cloud):
1. Push this repo to GitHub
2. Go to share.streamlit.io
3. Connect your GitHub and select this repo
4. Done — live URL you can share on your CV!

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 🙋 About

Built as a portfolio project demonstrating REST API integration, data processing with pandas, interactive data visualisation, and software testing with mocked dependencies.
