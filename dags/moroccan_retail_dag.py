from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# إضافة المسارات المرفقة
sys.path.append('/opt/airflow/plugins')

def run_etl_job():
    from src.retail_etl.pipeline import run_end_to_end_pipeline
    run_end_to_end_pipeline()

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 10, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'moroccan_retail_daily_etl',
    default_args=default_args,
    description='Daily ETL Pipeline for Moroccan Retail Data Warehousing',
    schedule_interval='0 2 * * *',  # تشغيل يومي الساعة 2 صباحاً
    catchup=False,
) as dag:

    execute_etl = PythonOperator(
        task_id='run_full_retail_etl',
        python_callable=run_etl_job,
    )

    execute_etl