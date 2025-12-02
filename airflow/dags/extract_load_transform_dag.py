from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import timedelta
import os
import pendulum
import sys
from pathlib import Path
from ingestion.extract_pipeline import run_ingestion


# CONFIG
TICKERS = ['NVDA','AAPL','MSFT','GOOGL','META','TSLA','LLY',
           'UNH','WMT','INTC','PEP','GE','GEV','ORCL','DIS','LEU',
           'NFLX','CRM','JNJ','NVO','KO','AMZN','PG','V']
BUCKET = os.getenv("BUCKET_NAME")
PROJECT = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("GCP_DATASET")
BRONZE_TABLE = os.getenv("GCP_BRONZE_LAYER")
DBT_DIR = os.getenv("DBT_DIR")

# DAG DEFINITION
default_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

start = pendulum.now("Europe/Berlin").subtract(minutes=10)
# start = pendulum.datetime(2024, 1, 1, tz="UTC")


with DAG(
    dag_id="extract_and_load_to_bronze_layer",
    default_args=default_args,
    description="Fetch stock prices → Parquet → GCS → BigQuery Bronze Layer",
    schedule="*/10 * * * *",   # every 10 minutes
    start_date=start,
    catchup=False,
    max_active_runs=1,
    tags=["stockpilot", "ingestion"]
) as dag:
    date = "{{ ds }}"
    # 1) Extract -> Parquet -> GCS
    extract_to_gcs = PythonOperator(
        task_id="extract_to_gcs",
        python_callable=run_ingestion,
        op_kwargs={
        "tickers": TICKERS,
        "period_": "1d",
        "interval_": "1m"
        }
    )

    # 2) Load Bronze (GCS -> BigQuery)
    load_to_bronze_layer = GCSToBigQueryOperator(
        task_id="load_to_bronze_layer",
        bucket=BUCKET,
        source_objects=[f"raw/{date}/*.parquet"],
        destination_project_dataset_table=f"{PROJECT}.{DATASET}.{BRONZE_TABLE}",
        source_format="PARQUET",
        write_disposition="WRITE_APPEND"  # 'WRITE_TRUNCATE' for daily batch
    )

    # 3) DBT Run (Bronze -> Silver & Silver -> Gold)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir $DBT_DIR'
    )

    # 4) DBT Test (Bronze -> Silver & Silver -> Gold)
    dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='dbt test --project-dir $DBT_DIR'
    )

    # Dependency
    extract_to_gcs >> load_to_bronze_layer >> dbt_run >> dbt_test
