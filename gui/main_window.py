from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, 
    QApplication, QHBoxLayout, QGridLayout, QMessageBox, QSizePolicy,
    QDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap, QColor
import os
import sys
import time
from utils.helpers import Location
from api.weather_service import WeatherService
import requests
from functools import lru_cache


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ICON_CACHE = {}

class LocationWorker(QThread):
    location_result = pyqtSignal(str)
    location_error = pyqtSignal(str)

    def run(self):
        try:
            city = Location.get_location()
            if city:
                self.location_result.emit(city)
            else:
                self.location_error.emit("Could not retrieve location coordinates.")
        except Exception as e:
            self.location_error.emit(f"Location error: {str(e)}")

class WeatherWorker(QThread):
    weather_result = pyqtSignal(dict)
    forecast_result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, city):
        super().__init__()
        self.city = city
        self.weather_service = WeatherService()

    def run(self):
        try:
            weather_data = self.weather_service.get_weather_data(self.city)
            if weather_data:
                self.weather_result.emit(weather_data)
                
                forecast_data = self.weather_service.get_forecast_data(self.city)
                if forecast_data:
                    self.forecast_result.emit(forecast_data)
            else:
                self.error.emit(f"Could not find weather data for {self.city}.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

def get_icon_path(icon_url):
    if "http" in icon_url:
        icon_url = icon_url.split("/")[-1].split(".")[0]
    return os.path.join("assets", "weather_icons", f"{icon_url}.png")

class IconLoader(QThread):
    icon_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, icon_urls):
        super().__init__()
        self.icon_urls = icon_urls
        os.makedirs(os.path.join("assets", "weather_icons"), exist_ok=True)

    def run(self):
        for url in self.icon_urls:
            if url in ICON_CACHE:
                self.icon_loaded.emit(url, ICON_CACHE[url])
            else:
                icon_url = url.split("/")[-1].split(".")[0]
                local_path = get_icon_path(icon_url)

                if os.path.exists(local_path):
                    icon_pixmap = QPixmap(local_path)
                    ICON_CACHE[url] = icon_pixmap
                    self.icon_loaded.emit(url, icon_pixmap)
                else:
                    try:
                        icon_response = requests.get(url)
                        if icon_response.status_code == 200:
                            icon_data = icon_response.content
                            icon_pixmap = QPixmap()
                            icon_pixmap.loadFromData(icon_data)
                            ICON_CACHE[url] = icon_pixmap
                            icon_pixmap.save(local_path, "PNG")
                            self.icon_loaded.emit(url, icon_pixmap)
                    except Exception as e:
                        print(f"Error loading icon from {url}: {str(e)}")

class CustomErrorDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")  # Sin título para un aspecto más minimalista
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Sin bordes de ventana
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fondo transparente
            
        # Configuración principal
        self.setFixedSize(400, 250)
            
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor con bordes redondeados
        self.container = QWidget()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(20)
            
        # Icono de error
        icon_layout = QHBoxLayout()
        error_icon = QLabel()
        error_icon.setFixedSize(50, 50)
            
        # Crear un icono personalizado usando un SVG en línea
        svg_icon = '''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF5252">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        '''
        pixmap = QPixmap()
        pixmap.loadFromData(bytearray(svg_icon, encoding='utf-8'))
        error_icon.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_layout.addWidget(error_icon, 0, Qt.AlignmentFlag.AlignCenter)
        container_layout.addLayout(icon_layout)
            
        # Texto de error
        error_text = QLabel("Error")
        error_text.setObjectName("errorTitle")
        error_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(error_text)
            
        # Mensaje detallado
        message_label = QLabel(message)
        message_label.setObjectName("errorMessage")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        container_layout.addWidget(message_label)
            
        # Espaciador para empujar el botón hacia abajo
        container_layout.addSpacing(10)
            
        # Botón OK
        ok_button = QPushButton("Aceptar")
        ok_button.setObjectName("okButton")
        ok_button.setFixedHeight(40)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.clicked.connect(self.accept)
        container_layout.addWidget(ok_button)
            
        # Añadir el contenedor al layout principal
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
            
        # Aplicar estilos
        self.setStyleSheet("""
            #container {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
                
            #errorTitle {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #333333;
            }
                
            #errorMessage {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #666666;
                margin-bottom: 10px;
            }
                
            #okButton {
                background-color: #ff5252;
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
            }
                
            #okButton:hover {
                background-color: #ff6b6b;
            }
                
            #okButton:pressed {
                background-color: #e04545;
            }
        """)
            
        # Efectos de sombra para una apariencia más moderna
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
    def showEvent(self, event):
        """Animación de aparición suave"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        super().showEvent(event)
        
    def mousePressEvent(self, event):
        """Permite arrastrar la ventana sin bordes"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        
    def mouseMoveEvent(self, event):
        """Mover la ventana al arrastrar"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPos)
            event.accept()

class WeatherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = False
        self.current_weather_condition = None
        self.dark_mode_button = QPushButton()
        self.dark_mode_button.setCheckable(True)
        icon_path = resource_path("assets/dark_mode.png")
        self.dark_mode_button.setIcon(QIcon(icon_path))
        self.weather_city_label = QLabel()
        self.weather_country_label = QLabel()
        self.weather_temp_label = QLabel()
        self.weather_description_label = QLabel()
        self.weather_humidity_label = QLabel()
        self.weather_wind_speed_label = QLabel()
        self.weather_icon = QLabel()
        self.city_input = QLineEdit()
        self.city_button = QPushButton("Get Weather")
        self.weather_label = QLabel("Weather Information")
        self.forecast_label = QLabel("Forecast Information")
        self.status_label = QLabel("Loading...")

        self.weather_panel = QWidget()
        self.weather_panel.setObjectName("weather_panel")

        self.forecast_icons = {}
        self.is_loading = False

        self.weather_grid = QGridLayout()
        self.forecast_grid = QGridLayout()
        self.forecast_grid.setObjectName("forecast_grid")
        self.top_layout = QHBoxLayout()

        self.initializeGUI()
        self.create_layout()
        self.setup_connections()

        self.location_worker = None
        self.weather_worker = None
        self.icon_loader = None

        self.weather_cache = {}
        self.last_update = {}
        self.cache_fresh_time = 60 * 10 # 10 minutes

        self.load_stylesheet()

        QTimer.singleShot(100, self.show_ip_weather) # A little delay to allow the GUI to load before fetching the weather data

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

        self.weather_city_label.setObjectName("city_name")
        self.weather_country_label.setObjectName("country_name")
        self.weather_temp_label.setObjectName("weather_temp_label")
        self.weather_description_label.setObjectName("weather_value")
        self.weather_humidity_label.setObjectName("weather_value")
        self.weather_wind_speed_label.setObjectName("weather_value")
        self.weather_icon.setObjectName("weather_icon")
        self.weather_label.setObjectName("weather_title")
        self.forecast_label.setObjectName("forecast_title")
        self.status_label.setObjectName("status_label")

        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.forecast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.city_input.setPlaceholderText("Enter city name")

    def setup_connections(self):
        self.city_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

    def create_layout(self):
        main_layout = QVBoxLayout()

        # Create the top layout (city, country, and input field)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.top_layout.addWidget(self.weather_city_label)
        self.top_layout.addWidget(self.weather_country_label)
        self.top_layout.addStretch(1)
        self.top_layout.addWidget(self.dark_mode_button)
        self.top_layout.addWidget(self.city_input)
        self.top_layout.addWidget(self.city_button)

        #Create status label
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        self.status_label.hide()

        #Create middle layout (weather information)
        mid_layout = QVBoxLayout(self.weather_panel)
        mid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mid_layout.addWidget(self.weather_label)
        mid_layout.addStretch(1)

        #config weather grid layout
        self.weather_grid.setObjectName("weather_grid")
        self.weather_grid.addWidget(self.weather_temp_label, 0, 0)
        self.weather_grid.addWidget(self.weather_description_label, 0, 1)
        self.weather_grid.addWidget(self.weather_humidity_label, 1, 0)
        self.weather_grid.addWidget(self.weather_wind_speed_label, 1, 1)
        self.weather_grid.addWidget(self.weather_icon, 0, 2, 2, 1)

        mid_layout.addLayout(self.weather_grid)
        mid_layout.addStretch(1)

        #Create the bottom layout (forecast information)
        forecast_container = QWidget()
        forecast_container.setObjectName("forecast_container")
        forecast_layout = QVBoxLayout(forecast_container)
        botton_layout = QVBoxLayout()
        botton_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        forecast_layout.addWidget(self.forecast_label)

        self.forecast_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forecast_layout.addLayout(self.forecast_grid)
        botton_layout.addWidget(forecast_container)
        botton_layout.addStretch(1)

        #Add all layouts to the main layout
        main_layout.addLayout(self.top_layout)
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.weather_panel)
        main_layout.addLayout(botton_layout)
        self.setLayout(main_layout)

    def update_weather_display(self, current_weather):
        #Update the weather information labels
        if current_weather:
            self.weather_city_label.setText(f"{current_weather['city_name']},")
            self.weather_country_label.setText(current_weather["country"])
            self.weather_temp_label.setText(f"{current_weather['temperature']}°C")
            self.weather_description_label.setText(current_weather["description"])
            self.weather_humidity_label.setText(f"Humidity: {current_weather['humidity']}%")
            self.weather_wind_speed_label.setText(f"Wind Speed: {current_weather['wind_speed']} km/h")

        #icon will load in Icon_loader thread to improve performance
        if "icon_url" in current_weather:
            self.collect_and_load_icons([current_weather["icon_url"]])

        if "description" in current_weather:
            self.apply_weather_style(current_weather["description"])

    def show_ip_weather(self):
        self.location_worker = LocationWorker()
        self.location_worker.location_result.connect(self.on_location_detected)
        self.location_worker.location_error.connect(self.on_location_error)
        self.location_worker.start()

    def on_location_detected(self, city):
        self.get_weather_for_city(city)

    def on_location_error(self, error_message):
        self.show_error_message(error_message)
        self.hide_loading()

    def get_weather_for_city(self, city):
        self.city_input.clear()
        if city in self.weather_cache and time.time() - self.last_update.get(city, 0) < self.cache_fresh_time:
            weather_data = self.weather_cache[city].get("weather")
            forecast_data = self.weather_cache[city].get("forecast")

            if weather_data:
                self.update_weather_display(weather_data)

            if forecast_data:
                self.update_forecast_display(forecast_data)
                icon_urls = [item["icon_url"] for item in forecast_data if "icon_url" in item]
                if weather_data and "icon_url" in weather_data:
                    icon_urls.append(weather_data["icon_url"])
                if icon_urls:
                    self.collect_and_load_icons(icon_urls)

            self.hide_loading()
            return
        
        self.show_loading(f"Loading weather data for {city}...")

        self.weather_worker = WeatherWorker(city)
        self.weather_worker.weather_result.connect(self.on_weather_received)
        self.weather_worker.forecast_result.connect(self.on_forecast_received)
        self.weather_worker.error.connect(self.on_weather_error)
        self.weather_worker.finished.connect(self.on_worker_finished)

        self.weather_worker.start()

    def on_weather_received(self, weather_data):
        city = weather_data["city_name"]
        if city not in self.weather_cache:
            self.weather_cache[city] = {}

        self.weather_cache[city]["weather"] = weather_data
        self.last_update[city] = time.time()

        self.update_weather_display(weather_data)

    def on_forecast_received(self, forecast_data):
        if forecast_data:
            city = self.weather_worker.city
            if city not in self.weather_cache:
                self.weather_cache[city] = {}

            self.weather_cache[city]["forecast"] = forecast_data

            self.update_forecast_display(forecast_data)

            icon_urls = [item.get('icon_url') for item in forecast_data if 'icon_url' in item]
            if city in self.weather_cache and "weather" in self.weather_cache[city]:
                weather_data = self.weather_cache[city]["weather"]
                if weather_data and "icon_url" in weather_data:
                    icon_urls.append(weather_data["icon_url"])

            if icon_urls:
                self.collect_and_load_icons(icon_urls)

    def on_weather_error(self, error_message):
        self.show_error_message(error_message)
        self.hide_loading()

    def on_worker_finished(self):
        self.hide_loading()

    def collect_and_load_icons(self, icon_urls):
        if not icon_urls:
            return

        self.icon_loader = IconLoader(icon_urls)
        self.icon_loader.icon_loaded.connect(self.on_icon_loaded)
        self.icon_loader.start()

    def on_icon_loaded(self, url, pixmap):
        if hasattr(self, "weather_worker") and self.weather_worker and hasattr(self.weather_worker, "city"):
            city = self.weather_worker.city
            if city in self.weather_cache:
                weather_data = self.weather_cache[city].get("weather")
                if weather_data and weather_data.get("icon_url") == url:
                    self.weather_icon.setPixmap(pixmap)
                    
        for date_label, icon_dict in self.forecast_icons.items():
            if icon_dict['url'] == url:
                icon_dict['label'].setPixmap(pixmap)

    def update_forecast_display(self, current_forecast):
        if not current_forecast:
            return

        # Clear the previous forecast widgets
        for i in reversed(range(self.forecast_grid.count())):
            widget = self.forecast_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.forecast_icons = {}
            
        for i, item in enumerate(current_forecast, 1):
            date_label = QLabel(item.get("date", ""))
            date_label.setObjectName("forecast_date")
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            min_temp_label = QLabel(f"{item.get('temp_min', '')}°C")
            min_temp_label.setObjectName("weather_value")
            min_temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            max_temp_label = QLabel(f"{item.get('temp_max', '')}°C")
            max_temp_label.setObjectName("weather_value")
            max_temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            forecast_icon = QLabel()
            forecast_icon.setObjectName("forecast_icon")
            forecast_icon.setMinimumSize(70, 70)
            forecast_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if self.is_dark_mode:
                for widget in [date_label, min_temp_label, max_temp_label, forecast_icon]:
                    widget.setProperty("darkMode", "true")
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)

            if "description" in item:
                weather_condition = self.get_weather_condition(item["description"])
                date_label.setProperty("weather_condition", weather_condition)
                min_temp_label.setProperty("weather_condition", weather_condition)
                max_temp_label.setProperty("weather_condition", weather_condition)

                for label in [date_label, min_temp_label, max_temp_label]:
                    label.style().unpolish(label)
                    label.style().polish(label)

            if "date" in item and "icon_url" in item:
                self.forecast_icons[item["date"]] = {
                    "label": forecast_icon,
                    "url": item["icon_url"]
                }

            date_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            min_temp_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            max_temp_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            forecast_icon.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            self.forecast_grid.addWidget(date_label, 0, i)
            self.forecast_grid.addWidget(max_temp_label, 1, i)
            self.forecast_grid.addWidget(min_temp_label, 2, i)
            self.forecast_grid.addWidget(forecast_icon, 3, i)

        for widget in self.findChildren(QWidget, "forecast_container"):
            if self.is_dark_mode:
                widget.setProperty("darkMode", "true")
            else:
                widget.setProperty("darkMode", "false")
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        self.forecast_grid.setColumnStretch(0, 0)
        for i in range(1, len(current_forecast) + 1):
            self.forecast_grid.setColumnStretch(i, 1)
        
    def get_weather(self):
        city_name = self.city_input.text().strip()
        if city_name:
            self.get_weather_for_city(city_name)
        else:
            self.show_error_message("City not found. Please check the name and try again.")

    def show_loading(self, message="Loading..."):
        self.is_loading = True
        self.status_label.setText(message)
        self.status_label.show()
        self.city_button.setEnabled(False)
        self.city_input.setEnabled(False)
        QApplication.processEvents()

    def hide_loading(self):
        self.is_loading = False
        self.status_label.hide()
        self.city_button.setEnabled(True)
        self.city_input.setEnabled(True)
        QApplication.processEvents()
        
    def toggle_dark_mode(self):
        self.is_dark_mode = self.dark_mode_button.isChecked()
        if self.is_dark_mode:
            icon_path = resource_path("assets/light_mode.png")
            self.dark_mode_button.setIcon(QIcon(icon_path))
            self.setProperty("darkMode", "true")
        else:
            icon_path = resource_path("assets/dark_mode.png")
            self.dark_mode_button.setIcon(QIcon(icon_path))
            self.setProperty("darkMode", "false")
       
        for widget in self.findChildren(QWidget):
            widget.setProperty("darkMode", "true" if self.is_dark_mode else "false")
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        qapp = QApplication.instance()
        qapp.setStyleSheet(qapp.styleSheet())

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


        if self.current_weather_condition:
            self.apply_weather_style(self.current_weather_condition)

    def get_weather_condition_type(self, weather_description):
        weather_description = weather_description.lower()

        if "clear" in weather_description:
            weather_class = "weather-clear"
        elif "cloud" in weather_description:
            weather_class = "weather-clouds"
        elif "rain" in weather_description or "drizzle" in weather_description:
            weather_class = "weather-rain"
        elif "snow" in weather_description:
            weather_class = "weather-snow"
        elif "thunder" in weather_description or "storm" in weather_description:
            weather_class = "weather-thunderstorm"
        elif "mist" in weather_description or "fog" in weather_description or "haze" in weather_description:
            weather_class = "weather-mist"
        else:
            return "clouds"

    def apply_weather_style(self, weather_condition):
        self.current_weather_condition = weather_condition
        weather_type = self.get_weather_condition_type(weather_condition)
        
        for widget in [self.weather_temp_label, self.weather_description_label,
                       self.weather_humidity_label, self.weather_wind_speed_label]:
            widget.setProperty("weatherCondition", weather_type)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        if hasattr(self, "weather_panel"):
            self.weather_panel.setProperty("weatherCondition", weather_type)
            self.weather_panel.style().unpolish(self.weather_panel)
            self.weather_panel.style().polish(self.weather_panel)
            self.weather_panel.update()
        
        self.style().unpolish(self)
        self.style().polish(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.width()
        height = self.height()

        if width < 800:
            self.weather_city_label.setStyleSheet("font-size: 20px;")
            self.weather_country_label.setStyleSheet
            self.weather_temp_label.setStyleSheet("font-size: 36px;")
            self.weather_description_label.setStyleSheet("font-size: 16px;")
        else:
            self.weather_city_label.setStyleSheet("font-size: 24px;")
            self.weather_country_label.setStyleSheet("font-size: 22px;")
            self.weather_temp_label.setStyleSheet("font-size: 42px;")
            self.weather_description_label.setStyleSheet("font-size: 18px;")

        if height < 600:
            self.weather_label.setStyleSheet("font-size: 18px; padding-top: 10px; padding-bottom: 5px;")
            self.forecast_label.setStyleSheet("font-size: 18px; padding-top: 10px; padding-bottom: 5px;")
        else:
            self.weather_label.setStyleSheet("font-size: 20px; padding-top: 20px; padding-bottom: 10px;")
            self.forecast_label.setStyleSheet("font-size: 20px; padding-top: 20px; padding-bottom: 10px;")

    def show_error_message(self, message):
            self.hide_loading()
            dialog = CustomErrorDialog(message, self)
            dialog.exec()
                

