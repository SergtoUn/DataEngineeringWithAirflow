from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators.stage_redshift import StageToRedshiftOperator
from operators.load_fact import LoadFactOperator
from operators.load_dimension import LoadDimensionOperator
from operators.data_quality import DataQualityOperator
from airflow.operators import (PostgresOperator)

from helpers import SqlQueries

default_args = {
    'owner': 'Sergei Chaschin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('processing_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          template_searchpath = ['/home/workspace/airflow'],
          schedule_interval='@hourly')

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_events",
    s3_path = "s3://udacity-dend/log_data",
    json_path = "s3://udacity-dend/log_json_path.json"
    )

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_songs",
    s3_path="s3://udacity-dend/song_data",
    json_path="auto"
    )

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "songplays",
    append = False,
    query = SqlQueries.songplay_table_insert    
    )

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "users",
    append = False,
    query = SqlQueries.user_table_insert
    )

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "songs",
    append = False,
    query = SqlQueries.song_table_insert
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "artists",
    append = False,
    query = SqlQueries.artist_table_insert
    )

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "time",
    append = False,
    query = SqlQueries.time_table_insert
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag, 
    redshift_conn_id = "redshift",
    dq_checks=[{'table': 'songplays', 'check_sql': SqlQueries.songplays_table_check, 'expected_result': 0},
                {'table': 'songs', 'check_sql': SqlQueries.songs_table_check, 'expected_result': 0},
                {'table': 'artists', 'check_sql': SqlQueries.artists_table_check, 'expected_result': 0},
                {'table': 'users', 'check_sql': SqlQueries.users_table_check, 'expected_result': 0},
                {'table': 'time', 'check_sql': SqlQueries.time_table_check, 'expected_result': 0}
              ])

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift
stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table
load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table
load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks
run_quality_checks >> end_operator