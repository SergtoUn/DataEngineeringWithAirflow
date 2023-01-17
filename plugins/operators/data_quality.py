from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = "",
                 dq_checks = [],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        # self.conn_id = conn_id
        self.redshift_conn_id = redshift_conn_id
        self.dq_checks = dq_checks
    def execute(self, context):
        self.log.info('Running data quality tests')
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)  
        for dic in self.dq_checks:
            self.log.info(f"Testing the table {dic['table']}")
            actual_result = redshift.get_records(dic['check_sql'])
            if actual_result[0][0] == dic['expected_result']:
                self.log.info("The test is passed")    
            else:
                self.log.error(f"{actual_result}, {dic['expected_result']}")
                raise ValueError(f"Data quality check failed. The table is {dic['table']}")
            
        
