import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WeatherAPIService:
    BASE_URL = "http://api.weatherapi.com/v1/forecast.json"
    CURRENT_WEATHER_URL = "http://api.weatherapi.com/v1/current.json"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'WEATHER_API_KEY', None)
        if not self.api_key:
            raise ValueError("API key for WeatherAPI is missing!")

    def get_forecast(self, latitude: float, longitude: float, hours: int = 24) -> list | None:
        params = {
            "key": self.api_key,
            "q": f"{latitude},{longitude}",
            "days": 1,
            "aqi": "no",
            "alerts": "no"
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            forecast_hours = data["forecast"]["forecastday"][0]["hour"]
            limited_hours = forecast_hours[:min(hours, len(forecast_hours))]

            return [
                {
                    "time": hour["time"],
                    "wind_kph": hour["wind_kph"],
                    "wind_dir": hour["wind_dir"],
                    "condition": hour["condition"]["text"]
                }
                for hour in limited_hours
            ]
        except requests.RequestException as e:
            logger.error(f"Request error while fetching forecast: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Parsing error in forecast data: {e}")
            return None

    def get_current_weather(self, latitude: float, longitude: float) -> dict | None:
        params = {
            "key": self.api_key,
            "q": f"{latitude},{longitude}",
            "aqi": "no",
        }

        try:
            response = requests.get(self.CURRENT_WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            return {
                "temp_c": current.get("temp_c"),
                "wind_kph": current.get("wind_kph"),
                "wind_dir": current.get("wind_dir"),
                "condition": current.get("condition", {}).get("text")
            }
        except requests.RequestException as e:
            logger.error(f"Request error while fetching current weather: {e}")
            return None
        except KeyError as e:
            logger.error(f"Parsing error in current weather data: {e}")
            return None


if __name__ == "__main__":
    API_KEY = "c67cac5327c741a7abb82828252505" 

    weather_service = WeatherAPIService(api_key=API_KEY)

    lat, lon = 44.4328, 26.1043

    print("Current weather:")
    current = weather_service.get_current_weather(lat, lon)
    print(current)

