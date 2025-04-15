from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dags')))

from create_sql_tables import run_table_creation
from merge import run_etl

with DAG("local_pg_workflow",
         schedule_interval=None,
         catchup=False,
         tags=["local", "postgres"],
         description="Run SQL scripts using local Postgres") as dag:

    create_tables = PythonOperator(
        task_id='create_tables',
        python_callable=run_table_creation
    )

    merge_data = PythonOperator(
        task_id='merge_data',
        python_callable=run_etl
    )

    create_tables >> merge_data