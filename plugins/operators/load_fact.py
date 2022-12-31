from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = "",
                 table = "",
                 append = False,
                 query = "",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
                
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.append = append
        self.query = query

        
    def execute(self, context):
        #self.log.info('LoadFactOperator not implemented yet')
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        if not self.append:
            self.log.info("Delete {} dimension table".format(self.table))
            redshift.run("DELETE FROM {}".format(self.table))
            
        self.log.info("Insert data from staging table into {} fact table".format(self.table))
        insert_query = f"INSERT INTO {self.table} \n{self.query}"
        self.log.info(f"Running sql: \n{insert_query}")
        redshift.run(insert_query)
        self.log.info(f"Data is inserted into {self.table}")