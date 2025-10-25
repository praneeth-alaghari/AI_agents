import requests
from langchain_core.tools import tool

OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
GEOCODING_BASE = "https://geocoding-api.open-meteo.com/v1"


@tool
def get_forecast_open_meteo(city: str, days: int = 3) -> str:
    """
    Get weather forecast for the next N days using Open-Meteo (no API key required).
    Provides daily high/low temperatures and precipitation forecasts.
    Use this when users ask about future weather, upcoming days, or weekly forecasts.
    
    Args:
        city: Name of the city (e.g., 'Mumbai', 'Paris', 'New York')
        days: Number of days to forecast (1-7, default: 3)
    """
    try:
        # Limit days to valid range
        days = max(1, min(days, 7))
        
        # Step 1: Get coordinates for the city
        geocode_resp = requests.get(
            f"{GEOCODING_BASE}/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"}
        )
        
        if geocode_resp.status_code != 200:
            return f"Could not find location: {city}"
        
        geo_data = geocode_resp.json()
        if not geo_data.get("results"):
            return f"City not found: {city}"
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")
        
        # Step 2: Get forecast data
        weather_resp = requests.get(
            f"{OPEN_METEO_BASE}/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "timezone": "auto",
                "forecast_days": days
            }
        )
        
        if weather_resp.status_code != 200:
            return f"Could not fetch forecast for {city}"
        
        weather_data = weather_resp.json()
        daily = weather_data["daily"]
        
        forecast_text = f"📅 **{days}-Day Forecast for {city_name}, {country}**\n\n"
        
        # Weather code mapping (WMO codes - simplified)
        weather_codes = {
            0: "☀️ Clear sky",
            1: "🌤️ Mostly clear",
            2: "⛅ Partly cloudy",
            3: "☁️ Cloudy",
            45: "🌫️ Foggy",
            48: "🌫️ Foggy",
            51: "🌦️ Light drizzle",
            61: "🌧️ Light rain",
            63: "🌧️ Moderate rain",
            65: "🌧️ Heavy rain",
            71: "❄️ Light snow",
            73: "❄️ Moderate snow",
            75: "❄️ Heavy snow",
            95: "⛈️ Thunderstorm"
        }
        
        for i in range(min(days, len(daily["time"]))):
            date = daily["time"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            precip = daily["precipitation_sum"][i]
            weather_code = daily["weather_code"][i]
            condition = weather_codes.get(weather_code, "Unknown")
            
            forecast_text += f"**Day {i+1}** ({date}):\n"
            forecast_text += f"  {condition}\n"
            forecast_text += f"  🌡️ High: {max_temp}°C | Low: {min_temp}°C\n"
            forecast_text += f"  🌧️ Precipitation: {precip} mm\n\n"
        
        return forecast_text.strip()
        
    except Exception as e:
        return f"Error fetching forecast from Open-Meteo: {str(e)}"
