from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

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
        
        
        
        copy_sql = """
        COPY {} 
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        JSON '{}';
    """
        
        

    def execute(self, context):
        #self.log.info('StageToRedshiftOperator not implemented yet')
        redshift_hook = PostgresHook(self.redshift_conn_id)
        aws_hook = AwsHook(self.aws_conn_id)
        credentials = aws_hook.get_credentials()
        
        self.log.info("Clearing data from destination Redshift table")
        redshift_hook.run("DELETE FROM {}".format(self.table))
        self.log.info("Copying data from S3 to Redshift")
        
        formatted_query = StageToRedshiftOperator.copy_sql.format(
                self.table, 
                self.s3_path, 
                credentials.access_key,
                credentials.secret_key, 
                self.json_path
                )
        
        redshift_hook.run(formatted_query)
        




