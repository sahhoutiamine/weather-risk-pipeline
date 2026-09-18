from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


from app.extraction.extract_cities import extract_cities
from app.extraction.extract_weather import extract_all_weather
from app.transformation.clean_weather import WeatherCleaner
from app.transformation.feature_engineering import FeatureEngineering
from app.load.load_gold import GoldLoader
from app.utils.logger import logger


default_args = {
    "owner": "weather_ops",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}



def run_extract_cities():
    extract_cities()


def run_extract_weather():
    extract_all_weather()


def run_clean_weather():
    WeatherCleaner().run()


def run_feature_engineering():
    FeatureEngineering().run()


def run_load_gold():
    GoldLoader().run()


def run_refresh_dashboard():

    logger.info(
        "Gold data loaded into PostgreSQL. Streamlit dashboard will reflect "
        "the new data within its 5-minute cache TTL."
    )


with DAG(
    dag_id="weather_risk_pipeline",
    description="Bronze -> Silver -> Gold -> PostgreSQL pipeline for Moroccan delivery weather risk",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    max_active_runs=1,
    tags=["weather", "risk", "morocco"],
) as dag:

    extract_cities_task = PythonOperator(
        task_id="extract_cities",
        python_callable=run_extract_cities,
    )

    extract_weather_task = PythonOperator(
        task_id="extract_weather",
        python_callable=run_extract_weather,
    )

    clean_weather_task = PythonOperator(
        task_id="clean_weather",
        python_callable=run_clean_weather,
    )

    feature_engineering_task = PythonOperator(
        task_id="feature_engineering",
        python_callable=run_feature_engineering,
    )

    load_gold_task = PythonOperator(
        task_id="load_gold",
        python_callable=run_load_gold,
    )

    refresh_dashboard_task = PythonOperator(
        task_id="refresh_dashboard",
        python_callable=run_refresh_dashboard,
    )

    (
        extract_cities_task
        >> extract_weather_task
        >> clean_weather_task
        >> feature_engineering_task
        >> load_gold_task
        >> refresh_dashboard_task
    )
