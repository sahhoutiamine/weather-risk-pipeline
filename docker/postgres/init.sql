-- ==========================================
-- Weather Risk Pipeline Database Initialization
-- ==========================================


-- ==========================================
-- Cities table
-- Stores Moroccan cities and coordinates
-- ==========================================

CREATE TABLE IF NOT EXISTS cities (

    city_id SERIAL PRIMARY KEY,

    city_name VARCHAR(100) NOT NULL,

    country VARCHAR(50) DEFAULT 'Morocco',

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT unique_city_location
        UNIQUE(city_name, latitude, longitude)

);



-- ==========================================
-- Forecast table
-- Stores raw weather predictions
-- ==========================================

CREATE TABLE IF NOT EXISTS forecast (

    forecast_id SERIAL PRIMARY KEY,


    city_id INTEGER NOT NULL,


    forecast_date DATE NOT NULL,


    temp_max DOUBLE PRECISION,

    temp_min DOUBLE PRECISION,


    precipitation_sum DOUBLE PRECISION,

    precipitation_probability INTEGER,


    wind_speed DOUBLE PRECISION,

    wind_gusts DOUBLE PRECISION,


    weather_code INTEGER,


    source VARCHAR(50) DEFAULT 'Open-Meteo',


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_forecast_city

        FOREIGN KEY(city_id)

        REFERENCES cities(city_id)

        ON DELETE CASCADE,


    CONSTRAINT unique_city_forecast_date

        UNIQUE(city_id, forecast_date)

);



-- ==========================================
-- Risk Score table
-- Stores business risk analysis
-- ==========================================

CREATE TABLE IF NOT EXISTS risk_score (

    risk_id SERIAL PRIMARY KEY,


    forecast_id INTEGER NOT NULL,


    risk_score INTEGER NOT NULL,


    risk_level VARCHAR(20),


    risk_reason TEXT,


    temperature_category VARCHAR(30),


    precipitation_category VARCHAR(30),


    wind_category VARCHAR(30),


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_risk_forecast

        FOREIGN KEY(forecast_id)

        REFERENCES forecast(forecast_id)

        ON DELETE CASCADE,


    CONSTRAINT check_risk_score_range

        CHECK(
            risk_score >= 0
            AND
            risk_score <= 100
        )

);



-- ==========================================
-- Indexes
-- Improves dashboard and SQL queries
-- ==========================================


CREATE INDEX IF NOT EXISTS idx_forecast_date

ON forecast(forecast_date);



CREATE INDEX IF NOT EXISTS idx_forecast_city

ON forecast(city_id);



CREATE INDEX IF NOT EXISTS idx_risk_score_value

ON risk_score(risk_score);



CREATE INDEX IF NOT EXISTS idx_risk_level

ON risk_score(risk_level);



-- ==========================================
-- Initialization message
-- ==========================================

DO $$

BEGIN

    RAISE NOTICE 'Weather Risk Pipeline database initialized successfully';

END $$;