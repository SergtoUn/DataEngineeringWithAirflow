from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (PostgresOperator)
from helpers import SqlQueries
import logging


AWS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')


default_args = {
    'owner': 'udacity',
    'depends_on_past': False,
    #'start_date': datetime(2019, 1, 12),
    'start_date': datetime.now(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('create_tables_dag',
          default_args=default_args,
          template_searchpath = ['/home/workspace/airflow'],
          description='Create staging data with Airflow',
          schedule_interval='@once')

create_tables = PostgresOperator(
    task_id="create_tables",
    dag=dag,
    postgres_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    sql='create_tables.sql'
    #sql='''SELECT * FROM pg_tables'''
)

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> create_tables
create_tables >> end_operator