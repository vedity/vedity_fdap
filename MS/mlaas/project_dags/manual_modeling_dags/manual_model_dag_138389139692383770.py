
#* Library Imports
import airflow
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.email_operator import EmailOperator

#* Relative Imports
from modeling.all_supervised_models import *



args = {'owner': 'airflow','start_date': airflow.utils.dates.days_ago(1),'provide_context': True,}

main_dag_id = "manual_model_dag_138389139692383770"

dag = DAG(dag_id=main_dag_id,default_args=args,catchup=False,schedule_interval = '@once',)



start_task = PythonOperator(task_id='start_pipeline',python_callable=start_pipeline,dag=dag,)


# Get model dict 

master_dict = {'model_id': [15], 'model_name': ['Decision_Tree_Classifier'], 'model_hyperparams': [{'criterion': 'gini', 'max_depth': '10', 'max_features': 'auto', 'min_impurity_decrease': '0.1', 'min_samples_leaf': '3'}], 'model_class_name': ['DecisionTreeClassificationClass'], 'algorithm_type': ['Multi']}

if len(master_dict) != 0:

    model_id = master_dict['model_id']
    model_name = master_dict['model_name']
    model_class_name = master_dict['model_class_name']
    model_hyperparams = master_dict['model_hyperparams']
    algorithm_type = master_dict['algorithm_type']

    for model_id,model_name, model_class_name, model_hyperparams,algorithm_type in zip(model_id,model_name, model_class_name, model_hyperparams,algorithm_type):
        dynamic_task = PythonOperator(task_id=model_name,
                                    python_callable=eval('supervised_models'),
                                    op_kwargs={'model_id':model_id,'model_name':model_name,
                                               'model_class_name':model_class_name,'algorithm_type': algorithm_type,
                                               'model_hyperparams':model_hyperparams},
                                    dag=dag)
        
        start_task >> dynamic_task
