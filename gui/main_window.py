from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, 
    QApplication, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
import sys
from utils.helpers import Location
from api.weather_service import WeatherService
import requests

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
    

class WeatherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeGUI()
        self.show_ip_weather()
        self.load_stylesheet()

    def load_stylesheet(self):
        try:
            with open("styles.css", "r") as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error al cargar el archivo CSS: {str(e)}")

    def initializeGUI(self):
        self.setWindowTitle("Weather App")

        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)

        self.setGeometry(100, 100, window_width, window_height)
        self.setMinimumSize(int(screen_width * 0.4), int(screen_height * 0.4))
        icon_path = resource_path("assets/app_icon.png")
        self.setWindowIcon(QIcon(icon_path))
    
    def show_ip_weather(self):
        city = Location.get_location()
        if city:
            weather_service = WeatherService()
            current_weather = weather_service.get_weather_data(city)
            current_forecast = weather_service.get_forecast_data(city)
            if current_weather:
                self.weather_city_label = QLabel(f"{current_weather["city_name"]},")
                self.weather_city_label.setObjectName("city_name")
                self.weather_country_label = QLabel(current_weather["country"])
                self.weather_country_label.setObjectName("country_name")
                self.weather_temperature_label = QLabel(f"{current_weather['temperature']}°C")
                self.weather_temperature_label.setObjectName("weather_value")
                self.weather_description_label = QLabel(current_weather["description"])
                self.weather_description_label.setObjectName("weather_value")
                self.weather_humidity_label = QLabel(f"Humidity: {current_weather['humidity']}%")
                self.weather_humidity_label.setObjectName("weather_value")
                self.weather_wind_speed_label = QLabel(f"Wind Speed: {current_weather['wind_speed']} km/h")
                self.weather_wind_speed_label.setObjectName("weather_value")
                """ VER COMO MANEJAR EL ICONO DEL TIEMPO
                self.weather_icon = QLabel()
                icon_url = current_weather["icon_url"]
                icon_response = requests.get(icon_url)
                if icon_response.status_code == 200:
                    icon_data = icon_response.content
                    icon_pixmap = QPixmap()
                    icon_pixmap.loadFromData(icon_data)
                    self.weather_icon.setPixmap(icon_pixmap)
                else:
                    print("Error fetching weather icon")
                """

            
            #for item in current_weather:
            if current_weather:
                #REVISAR PORQUE DEVUELVE UNA LISTA Y TENGO QUE ASIGNAR
                #LA APP NO FUNCIONA HASTA SOLUCIONAR EL FOR
                self.forecast_city_label = QLabel(f"{current_weather["city_name"]},")
                self.forecast_city_label.setObjectName("city_name")
                self.forecast_country_label = QLabel(current_weather["country"])
                self.forecast_country_label.setObjectName("country_name")
                self.forecast_temperature_label = QLabel(f"{current_weather['temperature']}°C")
                self.forecast_temperature_label.setObjectName("weather_value")
                self.forecast_description_label = QLabel(current_weather["description"])
                self.forecast_description_label.setObjectName("weather_value")
                self.forecast_humidity_label = QLabel(f"Humidity: {current_weather['humidity']}%")
                self.forecast_humidity_label.setObjectName("weather_value")
                self.forecast_wind_speed_label = QLabel(f"Wind Speed: {current_weather['wind_speed']} km/h")
                self.forecast_wind_speed_label.setObjectName("weather_value")
                """ VER COMO MANEJAR EL ICONO DEL TIEMPO Y COMO FUNCIONA CON EL PRONOSTICO 
                Y LOS MULTIPLES ICONOS
                self.forecast_icon = QLabel()
                icon_url = current_forecast["icon_url"]
                icon_response = requests.get(icon_url)
                if icon_response.status_code == 200:
                    icon_data = icon_response.content
                    icon_pixmap = QPixmap()
                    icon_pixmap.loadFromData(icon_data)
                    self.forecast_icon.setPixmap(icon_pixmap)
                else:
                    print("Error fetching weather icon")
                """

                self.create_interaction()
        else:
            print("Could not retrieve location coordinates.")

    def create_interaction(self):
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        top_layout.addWidget(self.weather_city_label)
        top_layout.addWidget(self.weather_country_label)
        top_layout.addStretch(1)
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter city name")
        self.city_button = QPushButton("Get Weather", self)
        #self.city_button.clicked.connect(self.get_weather)
        top_layout.addWidget(self.city_input)
        top_layout.addWidget(self.city_button)

        mid_layout = QVBoxLayout()
        mid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.weather_label = QLabel("Weather Information")
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_label.setObjectName("weather_title")
        mid_layout.addWidget(self.weather_label)
        mid_layout.addStretch(1)

        weather_grid = QGridLayout()

        weather_grid.addWidget(self.weather_temperature_label, 0, 0)
        weather_grid.addWidget(self.weather_description_label, 0, 1)
        weather_grid.addWidget(self.weather_humidity_label, 1, 0)
        weather_grid.addWidget(self.weather_wind_speed_label, 1, 1)
        #weather_grid.addWidget(self.weather_icon, 0, 2) #Falta resolver el problema del icono

        mid_layout.addLayout(weather_grid)
        mid_layout.addStretch(1)

        #Forecast section, API version does not support forecast data
        bottom_layout = QVBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.forecast_label = QLabel("Forecast Information")
        self.forecast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.forecast_label.setObjectName("forecast_title")
        bottom_layout.addWidget(self.forecast_label)

        forecast_grid = QGridLayout()
        forecast_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addLayout(forecast_grid)
        #Forecast data will be added here when API supports it
        forecast_grid.addWidget(self.forecast_temperature_label, 0, 0)
        forecast_grid.addWidget(self.forecast_description_label, 0, 1)
        forecast_grid.addWidget(self.forecast_humidity_label, 1, 0)
        forecast_grid.addWidget(self.forecast_wind_speed_label, 1, 1)


        bottom_layout.addStretch(1)
        
        layout.addLayout(top_layout)
        layout.addLayout(mid_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    
        
    def get_forecast(self):
        city_name = self.city_input.text()
        if city_name:
            weather_service = WeatherService()
            current_weather = weather_service.get_weather_by_city(city_name)

            
                

