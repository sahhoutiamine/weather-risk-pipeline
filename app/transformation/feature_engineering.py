import os
import pandas as pd
import numpy as np

from app.config.settings import SILVER_PATH, GOLD_PATH
from app.utils.logger import logger



class FeatureEngineering :
    def __init__ (self) :
        self.df = None
        
    def load_silver (self) :
        
        file_path = os.path.join(SILVER_PATH, "weather_clean.csv")
        
        self.df = pd.read_csv(file_path)
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        logger.info("Silver dataset loaded successfully")
        
    def create_date_features(self):
        pass

    def create_temperature_category(self):
        pass

    def create_precipitation_category(self):
        pass

    def create_wind_category(self):
        pass

    def create_risk_score(self):
        pass

    def create_risk_level(self):
        pass

    def create_risk_reason(self):
        pass

    def create_operational_flags(self):
        pass

    def save_gold(self):
        pass

    def run(self):

        self.load_silver()

        self.create_date_features()

        self.create_temperature_category()

        self.create_precipitation_category()

        self.create_wind_category()

        self.create_temperature_range()