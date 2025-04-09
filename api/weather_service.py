import requests
from datetime import datetime
from config import Config


class WeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.base_url_forecast = "http://api.openweathermap.org/data/2.5/forecast"
        self.units = "metric"
        self.lang = "en"

    def get_weather_data(self, city):
        try:
            current_response = requests.get(
                f"{self.base_url}?q={city}&appid={self.api_key}&units={self.units}&lang={self.lang}"
                
            )

            if current_response.status_code == 404:
                print("City not found")
                return None

            if current_response.status_code != 200:
                print(f"Error fetching weather data: {current_response.status_code}")
                return None
            
            current_data = current_response.json()

            current = {
                "temperature": round(current_data["main"]["temp"]),
                "description": current_data["weather"][0]["description"].capitalize(),
                "humidity": current_data["main"]["humidity"],
                "wind_speed": round(current_data["wind"]["speed"] * 3.6, 1 ),
                "icon_url": f"http://openweathermap.org/img/wn/{current_data['weather'][0]['icon']}@2x.png",
                "city_name": current_data["name"],
                "country": current_data["sys"].get("country", "")
            }

            return current

        except Exception as e:
            print(f"Error fetching weather data:{e}")
            return None
        
    def get_forecast_data(self, city):
        try:
            forecast_response = requests.get(
                f"{self.base_url_forecast}?q={city}&appid={self.api_key}&units={self.units}&lang={self.lang}&cnt=40"
            )

            if forecast_response.status_code != 200:
                return []
            
            forecast_data = forecast_response.json()
            
            # Agrupar pronósticos por día
            daily_forecasts = {}
            
            for item in forecast_data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                day_str = dt.strftime("%Y-%m-%d")
                
                # Inicializar entrada para este día si no existe
                if day_str not in daily_forecasts:
                    daily_forecasts[day_str] = {
                        "date": dt.strftime("%a %d"),
                        "temp_min": float('9999'),  # Un valor alto inicial
                        "temp_max": float('-9999'),  # Un valor bajo inicial
                        "icon": None,
                        "icon_count": {},  # Para contar ocurrencias de cada icono
                    }
                
                # Actualizar mínimo y máximo
                temp = item["main"]["temp"]
                daily_forecasts[day_str]["temp_min"] = min(daily_forecasts[day_str]["temp_min"], item["main"]["temp_min"])
                daily_forecasts[day_str]["temp_max"] = max(daily_forecasts[day_str]["temp_max"], item["main"]["temp_max"])
                
                # Contar ocurrencias de cada icono
                icon = item['weather'][0]['icon']
                if icon not in daily_forecasts[day_str]["icon_count"]:
                    daily_forecasts[day_str]["icon_count"][icon] = 0
                daily_forecasts[day_str]["icon_count"][icon] += 1
            
            # Convertir el diccionario a una lista y seleccionar el icono más frecuente para cada día
            forecast = []
            for day_str, day_data in sorted(daily_forecasts.items())[:5]:  # Limitar a 5 días
                # Encontrar el icono más frecuente
                if day_data["icon_count"]:
                    most_common_icon = max(day_data["icon_count"].items(), key=lambda x: x[1])[0]
                    day_data["icon_url"] = f"http://openweathermap.org/img/wn/{most_common_icon}.png"
                
                # Redondear temperaturas
                day_data["temp_min"] = round(day_data["temp_min"])
                day_data["temp_max"] = round(day_data["temp_max"])
                
                # Eliminar datos temporales
                day_data.pop("icon_count", None)
                day_data.pop("icon", None)
                
                forecast.append(day_data)
            
            return forecast
            
        except Exception as e:
            print(f"Error al obtener datos del pronóstico: {str(e)}")
            return []
        