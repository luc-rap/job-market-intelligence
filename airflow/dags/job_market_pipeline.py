
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# Make the project directory available for imports
sys.path.insert(0, "/opt/project")


def run_adzuna_ingestion():
    from ingest_adzuna_jobs import APP_ID, APP_KEY, ingest_jobs

    if not APP_ID or not APP_KEY:
        raise ValueError("Missing Adzuna API credentials")

    ingest_jobs(max_pages=5)


with DAG(
    dag_id="job_market_pipeline",
    start_date=datetime(2026, 11, 12),
    schedule=None,
    catchup=False,
    tags=["job-market-intelligence"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_adzuna_jobs",
        python_callable=run_adzuna_ingestion,
    )
