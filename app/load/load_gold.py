import os
import pandas as pd
from sqlalchemy import text

from app.config.database import engine
from app.config.settings import GOLD_PATH
from app.utils.logger import logger


class GoldLoader :
    def __init__ (self) :
        self.df = None
        
        
    def load_gold(self) :
        file_path = os.path.join(GOLD_PATH, "weather_risk.csv")
        self.df = pd.read_csv(file_path)
        self.df['date'] = pd.to_datetime(self.df['date']).dt.date
        logger.info(f"Loaded {len(self.df)} rows from gold dataset")
        
        
    def upsert_city (self, conn, row) :
        result = conn.execute(
            text("""INSERT INTO cities (city_name, latitude, longitude)
                VALUES (:city_name, :latitude, :longitude)
                ON CONFLICT (city_name, latitude, longitude)
                DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                RETURNING city_id"""),
            {
                "city_name" : row["city"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
            }
        )
        return result.scalar()
    
    def upsert_forecast(self, conn, city_id, row):
        result = conn.execute(
            text("""
                INSERT INTO forecast (
                    city_id, forecast_date, temp_max, temp_min,
                    precipitation_sum, precipitation_probability,
                    wind_speed, wind_gusts, weather_code
                )
                VALUES (
                    :city_id, :forecast_date, :temp_max, :temp_min,
                    :precipitation_sum, :precipitation_probability,
                    :wind_speed, :wind_gusts, :weather_code
                )
                ON CONFLICT (city_id, forecast_date)
                DO UPDATE SET
                    temp_max = EXCLUDED.temp_max,
                    temp_min = EXCLUDED.temp_min,
                    precipitation_sum = EXCLUDED.precipitation_sum,
                    precipitation_probability = EXCLUDED.precipitation_probability,
                    wind_speed = EXCLUDED.wind_speed,
                    wind_gusts = EXCLUDED.wind_gusts,
                    weather_code = EXCLUDED.weather_code,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING forecast_id
            """),
            {
                "city_id": city_id,
                "forecast_date": row["date"],
                "temp_max": row["temp_max"],
                "temp_min": row["temp_min"],
                "precipitation_sum": row["precipitation"],
                "precipitation_probability": row["precip_probability"],
                "wind_speed": row["wind_speed"],
                "wind_gusts": row["wind_gust"],
                "weather_code": row["weather_code"],
            }
        )
        return result.scalar()

    def upsert_risk_score(self, conn, forecast_id, row):
        conn.execute(
            text("""
                INSERT INTO risk_score (
                    forecast_id, risk_score, risk_level, risk_reason,
                    temperature_category, precipitation_category, wind_category
                )
                VALUES (
                    :forecast_id, :risk_score, :risk_level, :risk_reason,
                    :temperature_category, :precipitation_category, :wind_category
                )
                ON CONFLICT (forecast_id)
                DO UPDATE SET
                    risk_score = EXCLUDED.risk_score,
                    risk_level = EXCLUDED.risk_level,
                    risk_reason = EXCLUDED.risk_reason,
                    temperature_category = EXCLUDED.temperature_category,
                    precipitation_category = EXCLUDED.precipitation_category,
                    wind_category = EXCLUDED.wind_category,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                "forecast_id": forecast_id,
                "risk_score": int(row["risk_score"]),
                "risk_level": row["risk_level"],
                "risk_reason": row["risk_reason"],
                "temperature_category": row["temperature_category"],
                "precipitation_category": row["rain_category"],
                "wind_category": row["wind_category"],
            }
        )
        
    def run (self) :
        self.load_gold()
        count = 0
        with engine.begin() as conn :
            for _, row in self.df.iterrows() :
                city_id = self.upsert_city(conn, row)
                forecast_id = self.upsert_forecast(conn, city_id, row)
                self.upsert_risk_score(conn, forecast_id, row)
                count += 1
        logger.info(f"Loaded/updated {count} rows into PostgreSQL")
    

if __name__ == "__main__":
    loader = GoldLoader()
    loader.run()   
