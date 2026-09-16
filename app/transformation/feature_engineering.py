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
        self.df['day'] = self.df['date'].dt.day
        self.df['month'] = self.df['date'].dt.month
        self.df['weekday'] = self.df['date'].dt.day_name()
        self.df["forecast_day"] = (self.df['date'] - self.df['date'].min()).dt.days + 1

    def create_temperature_category(self):
        conditions = {
            (self.df['temp_max'] < 10), (self.df['temp_max'] >= 10) & (self.df['temp_max'] < 25), (self.df['temp_max'] >= 25) & (self.df['temp_max'] < 35), (self.df['temp_max'] >= 35) & (self.df['temp_max'] < 40), (self.df['temp_max'] >= 40)
        }
        choices = ["Cold", "Mild", "Warm", "Hot", "Extreme Heat"]
        
        
        self.df['temperature_category'] = np.select(conditions, choices, default="Unknown")

    def create_precipitation_category(self):
        conditions = {
            (self.df['precipitation'] == 0), (self.df['precipitation'] > 0) & (self.df['precipitation'] <= 5), (self.df['precipitation'] > 5) & (self.df['precipitation'] <= 20), (self.df['precipitation'] > 20) & (self.df['precipitation'] <=50), (self.df['precipitation'] > 50)
        }
        
        choices = [

            "No Rain",

            "Light Rain",

            "Moderate Rain",

            "Heavy Rain",

            "Extreme Rain"

        ]

        self.df["rain_category"] = np.select(conditions, choices, default="Unknown")

    def create_wind_category(self):

        conditions = [

            self.df["wind_speed"] < 20, (self.df["wind_speed"] >= 20) & (self.df["wind_speed"] < 40), (self.df["wind_speed"] >= 40) & (self.df["wind_speed"] < 60), self.df["wind_speed"] >= 60]


        choices = [

            "Calm",

            "Moderate",

            "Strong",

            "Extreme"

        ]


        self.df["wind_category"] = np.select(
            conditions,
            choices,
            default="Unknown"
        )
        
    def create_temperature_range(self):
        
     self.df["temp_range"] = (self.df['temp_max'] - self.df['temp_min'])
     
     
     def calculate_risk_score(self, row):

        score = 0

        # Temperature
        if row["temp_max"] >= 40:
            score += 25
        elif row["temp_max"] >= 35:
            score += 20
        elif row["temp_max"] >= 25:
            score += 10

        # Rain amount
        if row["precipitation"] > 50:
            score += 20
        elif row["precipitation"] > 20:
            score += 15
        elif row["precipitation"] > 5:
            score += 10
        elif row["precipitation"] > 0:
            score += 5

        # Rain probability
        if row["precip_probability"] >= 80:
            score += 15
        elif row["precip_probability"] >= 50:
            score += 10
        elif row["precip_probability"] >= 20:
            score += 5

        # Wind speed
        if row["wind_speed"] >= 60:
            score += 15
        elif row["wind_speed"] >= 40:
            score += 10
        elif row["wind_speed"] >= 20:
            score += 5

        # Wind gust
        if row["wind_gust"] >= 80:
            score += 15
        elif row["wind_gust"] >= 60:
            score += 10
        elif row["wind_gust"] >= 40:
            score += 5

        # Weather code
        if row["weather_code"] in [95, 96, 99]:
            score += 10
        elif row["weather_code"] in [61, 63, 65, 80, 81, 82]:
            score += 5

        return min(score, 100)


    def create_risk_score(self):
        self.df["risk_score"] = self.df.apply(
            self.calculate_risk_score,
            axis=1
        )

    def create_risk_level(self):

        conditions = [

            self.df["risk_score"] < 25,

            (self.df["risk_score"] >= 25)
            &
            (self.df["risk_score"] < 50),

            (self.df["risk_score"] >= 50)
            &
            (self.df["risk_score"] < 75),

            self.df["risk_score"] >= 75

        ]

        choices = [

            "Low",

            "Moderate",

            "High",

            "Critical"

        ]

        self.df["risk_level"] = np.select(
            conditions,
            choices,
            default="Unknown"
        )

    def create_risk_reason(self):

        reasons = []

        for _, row in self.df.iterrows():

            reason = []

            if row["temp_max"] >= 35:
                reason.append("High Temperature")

            if row["precipitation"] > 20:
                reason.append("Heavy Rain")

            if row["wind_speed"] >= 40:
                reason.append("Strong Wind")

            if row["wind_gust"] >= 60:
                reason.append("Strong Gusts")

            if row["weather_code"] in [95, 96, 99]:
                reason.append("Thunderstorm")

            if not reason:
                reason.append("Normal Conditions")

            reasons.append(", ".join(reason))

        self.df["risk_reason"] = reasons

    def create_operational_flags(self):

        self.df["is_risky"] = (
            self.df["risk_score"] >= 50
        )

        self.df["is_heatwave"] = (
            self.df["temp_max"] >= 40
        )

        self.df["is_heavy_rain"] = (
            self.df["precipitation"] > 20
        )

        self.df["is_strong_wind"] = (
            self.df["wind_speed"] >= 40
        )

    def save_gold(self):
        os.makedirs(GOLD_PATH, exist_ok=True)
        
        
        file_path = os.path.join(GOLD_PATH, "weather_risk.csv")
        
        self.df.to_csv(file_path, index=False)
        
        logger.info(f"Gold data saved: {file_path}")
        
        

    def run(self):

        self.load_silver()

        self.create_date_features()

        self.create_temperature_category()

        self.create_precipitation_category()

        self.create_wind_category()

        self.create_temperature_range()
        
        self.create_risk_score()

        self.create_risk_level()

        self.create_risk_reason()

        self.create_operational_flags()

        self.save_gold()