import os
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

URL_ITEC = os.getenv("URL_ITEC")
TOKEN = os.getenv("TOKEN")
FLIGHT_ID = "684f9718-2b7c-47c0-adb4-8987b91d72e9"  # id рейса
START_TIME = 1700438400  # unix, дальше переведется в дейтТайм
BUS_STOP_TIME = 60  # количество времени на остановке
ALLOWED_DISTANCE = 20  # Максимальное возможное расстояние от координаты маршрута до координаты остановки.
# Если остановок мало - увеличить значение

SPEED_MIN = 20      # Мин скорость движения
SPEED_MAX = 60      # Макс скорость движения
STOP_SPEED_MIN = 0  # Мин на остановке
STOP_SPEED_MAX = 0  # Макс на остановке

GRZ = 'АШДВАО'  # обычные требования для грз
STOP_SPEED = 0  # км/ч
