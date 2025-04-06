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
        lat, lon = Location.get_location()
        if lat and lon:
            weather_service = WeatherService()
            current_weather = weather_service.get_weather_by_coordinates(lat, lon)
            if current_weather:
                self.weather_city_label = QLabel(f"{current_weather["city_name"]},")
                self.weather_country_label = QLabel(current_weather["country"])
                self.weather_temperature_label = QLabel(f"{current_weather['temperature']}°C")
                self.weather_description_label = QLabel(current_weather["description"])
                self.weather_humidity_label = QLabel(f"Humidity: {current_weather['humidity']}%")
                self.weather_wind_speed_label = QLabel(f"Wind Speed: {current_weather['wind_speed']} km/h")
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
        mid_layout.addWidget(self.weather_label)
        mid_layout.addStretch(1) #Revisar si dejo esto o no

        weather_grid = QGridLayout()

        weather_grid.addWidget(self.weather_temperature_label, 0, 0)
        weather_grid.addWidget(self.weather_description_label, 0, 1)
        weather_grid.addWidget(self.weather_humidity_label, 1, 0)
        weather_grid.addWidget(self.weather_wind_speed_label, 1, 1)
        #weather_grid.addWidget(self.weather_icon, 0, 2) #Falta resolver el problema del icono

        mid_layout.addLayout(weather_grid)
        mid_layout.addStretch(1)
        
        layout.addLayout(top_layout)
        layout.addLayout(mid_layout)
        self.setLayout(layout)

    
        
    #def get_weather(self):
