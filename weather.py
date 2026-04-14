import requests
from datetime import datetime

class WeatherService:
    def __init__(self, api_key=None):
        # You can get a free API key from: https://openweathermap.org/api
        self.api_key = api_key or "4c841d833151e03cef03baabc6c7570f"  # Default test API key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.use_mock = True  # Use mock data if API fails

    def get_weather(self, city):
        """Get current weather data for a city"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use Celsius for temperature
            }
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "conditions": data["weather"][0]["main"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                # Return default values if API fails
                return {
                    "temperature": 25,
                    "humidity": 60,
                    "conditions": "Clear",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            print(f"Weather API error: {e}")
            # Return default values
            return {
                "temperature": 25,
                "humidity": 60,
                "conditions": "Clear",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def calculate_weather_impact(self, weather_data):
        """Calculate price adjustment factor based on weather conditions"""
        # Base multiplier
        multiplier = 1.0
        
        # Temperature impact
        temp = weather_data["temperature"]
        if temp > 35:  # Very hot
            multiplier *= 1.2  # Increase price due to storage/transport challenges
        elif temp < 5:  # Very cold
            multiplier *= 1.15  # Increase price due to storage/transport challenges
            
        # Weather conditions impact
        conditions = weather_data["conditions"].lower()
        weather_factors = {
            "rain": 1.1,    # Rain might affect transport
            "snow": 1.2,    # Snow significantly affects transport
            "storm": 1.25,  # Storms significantly affect transport
            "clear": 1.0,   # Ideal conditions
            "clouds": 1.0,  # Normal conditions
        }
        condition_factor = weather_factors.get(conditions, 1.0)
        multiplier *= condition_factor
        
        return round(multiplier, 2)