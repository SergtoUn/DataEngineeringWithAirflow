from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (PostgresOperator)
#from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
#                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries


AWS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')

default_args = {
    'owner': 'udacity',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('create_tables_dag',
          default_args=default_args,
          description='Create staging data with Airflow',
          schedule_interval='@once')

f = open(os.path.dirname(__file__) + '/../create_tables.sql')
create_tables_sql = f.read()
f.close()

sqlCommands = create_tables_sql.split(';')

for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            c.execute(command)
            print('Command {} executed', command)
        except:
            print("Command skipped")

create_tables = PostgresOperator(
    task_id="create_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql=create_tables_sql
)

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> create_tables
create_tables >> end_operator