import os
import json

import pandas as pd

from app.config.settings import (CITIES_BRONZE_PATH, WEATHER_BRONZE_PATH)

from app.utils.logger import logger



class WeatherCleaner :
    
    def __init__ (self) :
        self.cities_df = None
        self.weather_df = None
        self.df = None
        
        
    def load_cities (self) :
        self.cities_df = pd.read_csv(os.path.join(CITIES_BRONZE_PATH, "morocco_cities.csv"))
        
        
    def clean_cities (self) :
        self.cities_df = self.cities_df[['city', 'lat', 'lng']]
        self.cities_df.rename(columns={'lat' : 'latitude', 'lng' : 'longitude'}, inplace=True)
        self.cities_df.drop_duplicates(subset=['city', 'latitude', 'longitude'], inplace=True)
        self.cities_df['city'] = (self.cities_df['city'].str.strip())
        self.cities_df = self.cities_df[(self.cities_df['latitude'].between(21, 36)) & (self.cities_df['longitude'].between(-17, -1))]
        self.cities_df.dropna(subset=['city', 'latitude', 'longitude'], inplace=True)
    
    def load_weather (self) :
        records = []
        
        for date_folder in os.listdir(WEATHER_BRONZE_PATH) :
            folder_path = os.path.join(WEATHER_BRONZE_PATH, date_folder)
            
            if not os.path.isdir(folder_path) :
                continue 
            
            
            for file in os.listdir(folder_path) :
                if file.endswith('.json') :
                    file_path = os.path.join(folder_path, file)
                    
                    
                    with open(file_path, "r", encoding='utf-8') as f :
                        data = json.load(f)
                        city = file.replace('.json', '')
                        
                        daily = data['daily']
                        
                        
                        for i, date in enumerate(daily['time']) :
                            records.append({'city' : city, 'date' : date, 'temp_max' : daily['temperature_2m_max'][i], 'temp_min' : daily['temperature_2m_min'][i], 'precipitation' : daily['precipitation_sum'][i], 'precip_probability' : daily['precipitation_probability_max'][i], 'wind_speed' : daily['wind_speed_10m_max'][i], 'wind_gust' : daily['wind_gusts_10m_max'][i], 'weather_code' : daily['weather_code'][i]})
        
        self.weather_df = pd.DataFrame(records)
    
    def clean_weather (self) :
        
        self.weather_df['date'] = pd.to_datetime(self.weather_df['date'])
        numeric_columns = ["temp_max", "temp_min", "precipitation", "precip_probability", "wind_speed", "wind_gust", "weather_code"]
        
        for col in numeric_columns :
            self.weather_df[col] = pd.to_numeric(self.weather_df[col], errors='coerce')
        
        self.weather_df.drop_duplicates(subset=["city", "date"], inplace=True)
        for col in numeric_columns:
            self.weather_df[col].fillna(self.weather_df[col].median(), inplace=True)
            
        self.weather_df = self.weather_df[(self.weather_df["temp_max"] >= -50) & (self.weather_df["temp_max"] <= 60)]
        self.weather_df = self.weather_df[(self.weather_df["temp_min"] >= -50) & (self.weather_df["temp_min"] <= 50)]
        self.weather_df = self.weather_df[self.weather_df["temp_min"] <= self.weather_df["temp_max"]]
        self.weather_df = self.weather_df[self.weather_df["precipitation"] >= 0]
        self.weather_df = self.weather_df[self.weather_df["precip_probability"].between(0,100)]
        self.weather_df = self.weather_df[self.weather_df["wind_speed"] >= 0]
        self.weather_df = self.weather_df[self.weather_df["wind_gust"] >= 0]
        
            
        
    def merge_data (self) :
        self.df = self.weather_df.merge(self.cities_df, on='city', how='left')
        
        
    def save_silver(self) :
        file_path = "app/silver/weather_clean.csv"

        os.makedirs('app/silver', exist_ok=True)
        
        self.df.to_csv(file_path, index=False)
        
        logger.info(f"Silver data saved: {file_path}")
        
        
    def run(self):

        self.load_cities()

        self.clean_cities()

        self.load_weather()

        self.clean_weather()

        self.merge_data()

        self.save_silver()




if __name__ == "__main__" :
    cleaner = WeatherCleaner()
    cleaner.run()
