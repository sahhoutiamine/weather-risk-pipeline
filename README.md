# Weather Risk Pipeline — Moroccan Delivery Operations

A complete end-to-end data pipeline designed to extract, process, and analyze weather forecasts for Moroccan cities. This project helps a delivery and logistics company identify periods and locations with high weather-related risks (extreme heat, heavy rain, strong winds) to better anticipate operational disruptions.

The pipeline follows the **Bronze → Silver → Gold** architecture, is orchestrated by **Apache Airflow**, stored in **PostgreSQL**, and visualized via a **Streamlit Dashboard**, all containerized using **Docker Compose**.

---

## Architecture & Data Flow

1. **Extraction (Bronze)**: 
   - Fetches Moroccan cities and coordinates from SimpleMaps.
   - Queries the Open-Meteo API for daily weather forecasts (max/min temp, precipitation, wind speed/gusts, weather code) for each city.
   - Raw data is stored in `app/bronze/` (unchanged).
2. **Transformation (Silver)**:
   - Cleans and standardizes data types and dates.
   - Handles duplicates, checks for inconsistencies (e.g., `temp_min > temp_max`).
   - Merges city coordinates with weather data.
   - Saves to `app/silver/weather_clean.csv`.
3. **Feature Engineering (Gold)**:
   - Creates date features, temperature/rain/wind categories.
   - Calculates a **Weather Risk Score (0–100)** and assigns **Risk Levels** (Low, Medium, High, Critical).
   - Saves to `app/gold/weather_risk.csv`.
4. **Loading**:
   - Upserts (Insert/Update) the Gold data into a PostgreSQL database (`cities`, `forecast`, `risk_score` tables) using SQLAlchemy.
5. **Orchestration (Airflow)**:
   - The `weather_risk_pipeline` DAG runs daily, handling retries and task dependencies.
6. **Visualization (Streamlit)**:
   - Connects to PostgreSQL to display KPIs, interactive maps, risk trends, and detailed alert tables.

---

## Project Structure

```text
weather-risk-pipeline/
│
├── airflow/                         # Airflow DAGs and configurations
│   └── dags/
│       └── weather_risk_pipeline_dag.py
│
├── app/                             # Main application code
│   ├── bronze/                      # Raw data (untouched)
│   │   ├── cities/                  # morocco_cities.csv
│   │   └── weather_raw/             # YYYY-MM-DD/CityName.json
│   ├── silver/                      # Cleaned data
│   │   └── weather_clean.csv
│   ├── gold/                        # Feature engineered data
│   │   └── weather_risk.csv
│   ├── config/                      # Configuration files
│   │   ├── database.py              # SQLAlchemy engine setup
│   │   └── settings.py              # Path and environment settings
│   ├── extraction/                  # Bronze layer scripts
│   │   ├── extract_cities.py
│   │   └── extract_weather.py
│   ├── transformation/              # Silver & Gold layer scripts
│   │   ├── clean_weather.py
│   │   └── feature_engineering.py
│   ├── load/                        # Gold to PostgreSQL loader
│   │   └── load_gold.py
│   └── utils/                       # Utilities
│       └── logger.py
│
├── docker/                          # Docker initialization scripts (e.g., init.sql)
├── .env                             # Environment variables (DB credentials)
├── .env.example                     # Example environment file
├── .gitignore
├── docker-compose.yml               # Multi-container orchestration
├── requirements.txt                 # Python dependencies
└── README.md
```

## Tech Stack

- **Language**: Python 3.12
- **Data Processing**: Pandas, NumPy
- **Orchestration**: Apache Airflow
- **Database**: PostgreSQL, SQLAlchemy
- **Dashboard**: Streamlit, Plotly
- **Containerization**: Docker, Docker Compose

## Weather Risk Score Logic

The risk score (0–100) is calculated based on weighted thresholds across multiple weather variables:

| Variable | Condition | Points Added |
|---|---|---|
| Max Temp | ≥ 42°C | +35 |
| | ≥ 38°C | +25 |
| | ≥ 33°C | +15 |
| Precipitation | > 50 mm | +20 |
| | > 20 mm | +15 |
| Precip. Probability | ≥ 80% | +10 |
| Wind Speed | ≥ 60 km/h | +13 |
| Wind Gusts | ≥ 80 km/h | +12 |
| Weather Code | Thunderstorms (95, 96, 99) | +10 |

**Risk Levels:**
- Low: 0–20
- Medium: 21–40
- High: 41–70
- Critical: 71–100

## Getting Started

### Prerequisites

- Docker Desktop installed and running.
- Git (optional, for cloning).

### 1. Environment Setup

Copy the example environment file and fill in your PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env` with your desired database credentials:

```env
DB_USER=airflow
DB_PASSWORD=airflow
DB_HOST=postgres
DB_PORT=5432
DB_NAME=weather_risk
BASE_PATH=app
```

### 2. Build and Run Containers

From the project root, run:

```bash
docker compose up -d --build
```

This will start:
- PostgreSQL (port 5432)
- Airflow Webserver (port 8080) and Scheduler
- Streamlit Dashboard (port 8501)

### 3. Initialize the Database

Ensure the database schema is created. You can run the provided SQL script (if placed in `docker/`) or execute it manually via a DB client. The schema includes `cities`, `forecast`, and `risk_score` tables.

### 4. Trigger the Pipeline

Open Airflow at http://localhost:8080 (default login: `airflow` / `airflow`).

Find the DAG `weather_risk_pipeline`.

Unpause it and trigger a manual run (Play button).

The DAG will execute: `extract_cities` → `extract_weather` → `clean_weather` → `feature_engineering` → `load_gold` → `refresh_dashboard`.

### 5. Access the Dashboard

Open Streamlit at http://localhost:8501.

Use the sidebar to filter by city, date range, or risk level. The dashboard provides:

- **KPIs**: Total cities, max temperature, max precipitation, count of high/critical risk periods, and the highest risk city.
- **Map**: Color-coded map of Morocco showing risk levels per city.
- **Trends**: Time-series chart of risk scores per city.
- **Heatmap**: City vs. Date risk matrix.
- **Alerts**: Table of cities and dates with High/Critical risk.
