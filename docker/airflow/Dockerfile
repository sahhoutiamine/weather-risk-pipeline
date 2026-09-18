FROM apache/airflow:2.10.3-python3.12

USER root

# Nothing extra needed at OS level for this pipeline (no compiled deps beyond psycopg2-binary,
# which ships as a wheel already).

USER airflow

# Install only what the pipeline scripts need (pandas, sqlalchemy, psycopg2, requests, dotenv),
# constrained against Airflow's own compatibility matrix so we don't break its internal deps.
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.12.txt" \
    pandas \
    numpy \
    sqlalchemy \
    psycopg2-binary \
    requests \
    python-dotenv
