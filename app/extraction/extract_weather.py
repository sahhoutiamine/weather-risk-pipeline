import os
import json
import requests
import pandas as pd

from datetime import date


from app.config.settings import (WEATHER_BRONZE_PATH, CITIES_BRONZE_PATH)
from app.utils.logger import logger 

API_URL = ("https://api.open-meteo.com/v1/forecast")

def extract_city_weather (city_name, latitude, longitude) :
    params = {
        "latitude" : latitude,
        "longitude" : longitude,
        "daily" : ["temperature_2m_max","temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "weather_code"],
        "timezone" : "Africa/Casablanca"
    }
    
    try :
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "daily" not in data :
            raise Exception("Invalid API response!")
        
        today = str(date.today())
        folder = os.path.join(WEATHER_BRONZE_PATH, today)
        os.makedirs(folder, exist_ok=True)
        
        file_path = os.path.join(folder, f"{city_name}.json")
        
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            
            
        logger.info(f"{city_name} weather saved")
        
        
    except requests.Timeout :
        logger.error(f"{city_name}: timeout")
        
        
    except requests.HTTPError as er :
        logger.error(f"{city_name} : HTTP error {er}")
    
    except Exception as e :
        logger.error(f"{city_name} : {e}")
        


def extract_all_weather () :
    
    cities_file = os.path.join(CITIES_BRONZE_PATH, "morocco_cities.csv")
    logger.info("Reading cities CSV...")
    cities_df = pd.read_csv(cities_file)
    
    logger.info(f"{len(cities_df)} cities found")
    
    cities_df = cities_df.head(5)
    
    
    for _, row in cities_df.iterrows() :
        city_name = row['city']
        latitude = row['lat']
        longitude = row['lng']
        
        
        logger.info(f"Extracting weather for {city_name}")

        extract_city_weather(city_name, latitude, longitude)
        
    logger.info("Weather extraction completed.")
    
    
    
    
if __name__ == "__main__" :
    extract_all_weather()