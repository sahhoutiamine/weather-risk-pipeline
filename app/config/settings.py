import os 
from dotenv import load_dotenv



load_dotenv()

BASE_PATH = os.getenv("BASE_PATH", "app")

BRONZE_PATH = os.path.join(BASE_PATH, "bronze")

CITIES_BRONZE_PATH = os.path.join(BRONZE_PATH, "cities") 

WEATHER_BRONZE_PATH = os.path.join(BRONZE_PATH, "weather_raw")