import os 
import requests
import json
from datetime import date


from app.config.settings import WEATHER_BRONZE_PATH
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
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "daily" not in data :
            raise Exception("Invalid API response!")
        
        today = str(date.today())
        folder = os.path.join(WEATHER_BRONZE_PATH, today)
        os.makedirs(folder, exist_ok=True)
        
        file_path = os.path.join(folder, f"{city_name}.json")
        
        with open(file_path, "w") as file :
            json.dump(data, file, indent=4)
            
            
        logger.info(f"{city_name} weather saved")
        
        
    except requests.Timeout :
        logger.error(f"{city_name}: timeout")
        
        
    except requests.HTTPError as er :
        logger.error(f"{city_name} : HTTP error {er}")
    
    except Exception as e :
        logger.error(f"{city_name} : {e}")
        
        
        
if __name__ == "__main__" :
    extract_city_weather("Casablanca", 33.5731, -7.5898)