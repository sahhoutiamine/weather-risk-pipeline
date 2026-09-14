import requests
import os 

from app.config.settings import CITIES_BRONZE_PATH
from app.utils.logger import logger 

URL = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"


def extract_cities():
    logger.info("Starting cities extraction")
    try:
        response = requests.get(URL, timeout=20)
        response.raise_for_status()
        os.makedirs(CITIES_BRONZE_PATH, exist_ok=True)
        
        file_path = os.path.join(CITIES_BRONZE_PATH, "morocco_cities.csv")
        
        with open(file_path, "wb") as file :
            file.write(response.content)
        
        logger.info(f"Cities saved : {file_path}")
    
    except requests.Timeout :
        logger.error("SimpleMaps request timeout")
        
    except requests.HTTPError as er :
        logger.error(f"HTTP error : {er}")
    except Exception as e :
        logger.error(f"Unexpected error: {e}")
        
        
if __name__ == "__main__":
    extract_cities()