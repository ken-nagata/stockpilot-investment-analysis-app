FROM python:3.12.8-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1

ENV AIRFLOW_HOME=/app/airflow

# DBT
# $DEL_BEGIN
ENV DBT_DIR=$AIRFLOW_HOME/dbt
ENV DBT_TARGET_DIR=$DBT_DIR/target
ENV DBT_PROFILES_DIR=$DBT_DIR
ENV DBT_VERSION=1.9.1
# $DEL_END

WORKDIR $AIRFLOW_HOME

COPY scripts scripts

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --no-root

# --- Project files (dags, dbt, etc.) ---
COPY airflow/dags dags
COPY dbt dbt
COPY ingestion ingestion

# Install dbt dependencies
RUN poetry run dbt deps --project-dir dbt

RUN chmod +x ./scripts/entrypoint.sh
