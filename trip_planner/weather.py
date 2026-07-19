
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def geocode(place: str) -> dict | None:
    """Resolve a place name to lat/lon/timezone/display name."""
    try:
        r = requests.get(GEOCODE_URL, params={"name": place, "count": 1}, timeout=10)
        r.raise_for_status()
        results = r.json().get("results")
        if not results:
            return None
        top = results[0]
        return {
            "name": top.get("name"),
            "country": top.get("country"),
            "latitude": top["latitude"],
            "longitude": top["longitude"],
            "timezone": top.get("timezone", "auto"),
        }
    except (requests.RequestException, KeyError):
        return None


def get_forecast(latitude: float, longitude: float, days: int = 7) -> list[dict]:
    """Daily forecast: max/min temp (C), precipitation chance, weather code."""
    days = max(1, min(days, 16))  # Open-Meteo free tier supports up to 16 days
    try:
        r = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=10,
        )
        r.raise_for_status()
        daily = r.json().get("daily", {})
        out = []
        for i, date in enumerate(daily.get("time", [])):
            out.append({
                "date": date,
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precip_chance": daily["precipitation_probability_max"][i],
                "code": daily["weathercode"][i],
            })
        return out
    except (requests.RequestException, KeyError, IndexError):
        return []


WEATHER_CODES = {
    0: "☀️ Clear sky", 1: "🌤️ Mostly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
    45: "🌫️ Fog", 48: "🌫️ Fog", 51: "🌦️ Light drizzle", 53: "🌦️ Drizzle",
    55: "🌧️ Heavy drizzle", 61: "🌧️ Light rain", 63: "🌧️ Rain", 65: "🌧️ Heavy rain",
    71: "🌨️ Light snow", 73: "🌨️ Snow", 75: "❄️ Heavy snow", 80: "🌦️ Rain showers",
    81: "🌧️ Rain showers", 82: "⛈️ Violent showers", 95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm w/ hail", 99: "⛈️ Severe thunderstorm",
}


def describe_code(code: int) -> str:
    return WEATHER_CODES.get(code, "🌡️ Unknown")
