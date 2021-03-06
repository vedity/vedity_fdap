from common.utils.dynamic_dag.operators.template_operator import TemplateOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.dates import days_ago
import os
from pathlib import Path


class RestToTemplateWrapperOperator(TemplateOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script_dir = os.path.dirname(__file__)
        self.dynamic_dag_dir = os.environ.get(
            'DYNAMIC_DAG_DIR', '/usr/local/airflow/dags/project_dags')
        
    def execute(self, context):
        
        print("Trying to get parameters")
        
        conf = context["dag_run"].conf
        namespace = conf['namespace']
        dag_id = conf["dag_id"]
        template = conf['template']
        
        print("Got Parameters")
        
        Path(os.path.join(self.dynamic_dag_dir, namespace)).mkdir(parents=True, exist_ok=True)
        
        self.template_file_path = os.path.join(
            self.script_dir, '..', 'templates', template) 
        
        self.destination_file_path = os.path.join(self.dynamic_dag_dir, namespace, '{}.py'.format(dag_id))

        self.search_and_replace = {
            '#MASTER_DICT': conf["master_dict"],
            '#DAG_ID': '"'+dag_id+'"'
        }
        TemplateOperator.execute(self)