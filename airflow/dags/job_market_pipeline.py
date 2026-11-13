
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Make the project directory available for imports
sys.path.insert(0, "/opt/project")


def run_adzuna_ingestion():
    from ingest_adzuna_jobs import APP_ID, APP_KEY, ingest_jobs

    if not APP_ID or not APP_KEY:
        raise ValueError("Missing Adzuna API credentials")

    ingest_jobs(max_pages=10)


with DAG(
    dag_id="job_market_pipeline",
    start_date=datetime(2026, 11, 12),
    schedule="0 10,18 * * *",
    catchup=False,
    tags=["job-market-intelligence"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_adzuna_jobs",
        python_callable=run_adzuna_ingestion,
    )

    copy_task = SQLExecuteQueryOperator(
        task_id="copy_s3_into_snowflake",
        conn_id="snowflake_default",
        sql="""
            COPY INTO JOB_MARKET_INTELLIGENCE.RAW.RAW_ADZUNA_JOBS
                (RAW_DATA, SOURCE_FILE, LOADED_AT)
            FROM (
                SELECT
                    $1,
                    METADATA$FILENAME,
                    CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
                FROM @JOB_MARKET_INTELLIGENCE.RAW.ADZUNA_STAGE_TEMP
            )
            FILE_FORMAT = (
                FORMAT_NAME = 'JOB_MARKET_INTELLIGENCE.RAW.ADZUNA_JSON_FORMAT'
            )
            ON_ERROR = 'ABORT_STATEMENT';
        """,
    )

    ingest_task >> copy_task
