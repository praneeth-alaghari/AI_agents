# tools.py
import requests
from mcp_urls import MCP_WEATHER_URL
from langchain_core.tools import tool

MCP_WEATHER_URL = MCP_WEATHER_URL

@tool
def get_weather(city: str) -> str:
    """Call the MCP weather API. Once done also check the user's personal weather preferences to give tailored advice."""
    try:
        resp = requests.get(MCP_WEATHER_URL, params={"city": city})
        if resp.status_code == 200:
            return resp.json().get("weather", "Weather info not available.")
        else:
            return "I couldn't fetch the weather."
    except Exception:
        return "Error contacting the weather service."

if __name__ == "__main__":
    city = input("Enter city name: ")
    weather_info = get_weather(city)
    print(f"Weather in {city}: {weather_info}")