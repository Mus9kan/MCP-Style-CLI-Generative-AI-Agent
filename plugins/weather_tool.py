"""Sample weather plugin - demonstrates plugin architecture."""

from typing import Dict, Any, List
import requests

from cli_agent.tools.base import BaseTool
from cli_agent.tools.registry import register_tool


@register_tool
class WeatherTool(BaseTool):
    """Get current weather information for a location."""
    
    name = "get_weather"
    description = "Get current weather information for a specified city"
    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., 'London', 'New York')",
            },
            "units": {
                "type": "string",
                "description": "Temperature units: 'metric' (Celsius) or 'imperial' (Fahrenheit)",
                "default": "metric",
            },
        },
        "required": ["city"],
    }
    
    def execute(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather information for a city.
        
        Note: This requires a free API key from OpenWeatherMap.
        Set OPENWEATHER_API_KEY environment variable.
        """
        import os
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            return {
                "success": False,
                "error": "OPENWEATHER_API_KEY not set. Get free key from: https://openweathermap.org/api",
            }
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": units,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": f"{data['main']['temp']}°{'C' if units == 'metric' else 'F'}",
                "feels_like": f"{data['main']['feels_like']}°{'C' if units == 'metric' else 'F'}",
                "humidity": f"{data['main']['humidity']}%",
                "description": data["weather"][0]["description"],
                "wind_speed": f"{data['wind']['speed']} m/s",
            }
            
            return {
                "success": True,
                "weather": weather_info,
            }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to fetch weather: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}",
            }


@register_tool
class TimezoneTool(BaseTool):
    """Get current time for a timezone."""
    
    name = "get_time"
    description = "Get current time for a specified timezone"
    parameters = {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone name (e.g., 'America/New_York', 'Europe/London')",
            },
        },
        "required": ["timezone"],
    }
    
    def execute(self, timezone: str) -> Dict[str, Any]:
        """Get current time for a timezone."""
        try:
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            
            return {
                "success": True,
                "timezone": timezone,
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "date": current_time.strftime("%A, %B %d, %Y"),
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get time: {str(e)}",
            }
