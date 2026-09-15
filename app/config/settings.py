import os 
from dotenv import load_dotenv



load_dotenv()

BASE_PATH = os.getenv("BASE_PATH", "app")

BRONZE_PATH = os.path.join(BASE_PATH, "bronze")

SILVER_PATH = os.path.join(BASE_PATH, "silver")

GOLD_PATH = os.path.join(BASE_PATH, "gold")

CITIES_BRONZE_PATH = os.path.join(BRONZE_PATH, "cities") 

WEATHER_BRONZE_PATH = os.path.join(BRONZE_PATH, "weather_raw")