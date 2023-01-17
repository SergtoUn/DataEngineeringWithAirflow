from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    
    copy_sql = """
        COPY {} 
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        JSON '{}';
    """
    
    exec_time_sql = """
        COPY {} 
        FROM '{}'/'{}'/'{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        JSON '{}';
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials_id="",
                 table="",
                 s3_path="",
                 json_path="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_path = s3_path
        self.json_path=json_path
        self.execution_date = kwargs.get('execution_date')


    def execute(self, context):
        self.log.info('Getting credentials')
        redshift_hook = PostgresHook(self.redshift_conn_id)
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        
        self.log.info("Clearing data from destination Redshift table")
        redshift_hook.run("DELETE FROM {}".format(self.table))
        
        self.log.info("Copying data from S3 to Redshift")
        if (self.execution_date is None):
            final_query = StageToRedshiftOperator.copy_sql.format(
            self.table, 
            self.s3_path, 
            credentials.access_key,
            credentials.secret_key, 
            self.json_path
            )
            
           
        else:
            final_query = StageToRedshiftOperator.copy_sql.format(
            self.table, 
            self.s3_path,
            self.execution_date.strftime("%Y"),
            self.execution_date.strftime("%d"),
            credentials.access_key,
            credentials.secret_key, 
            self.json_path
            )
        
        redshift_hook.run(final_query)
        




