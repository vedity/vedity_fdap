'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Vipul Prajapati      25-JAN-2021           1.0         Initial Version 
 Mann Purohit         02-FEB-2021           1.1           

*/
'''
import airflow
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.email_operator import EmailOperator

### Import function from main file

from modeling.all_regressor import start_pipeline
from modeling.all_regressor import linear_regression_sklearn


args = {
'owner': 'airflow',
'start_date': airflow.utils.dates.days_ago(1),      
'provide_context': True,}


dag = DAG(
    dag_id='auto_regressor_pipeline',
    default_args=args,         
    catchup=False,                         
)

##### One dag for auto #########

t1 = PythonOperator(
    task_id='get_dataset_ids',
    python_callable=get_dataset_ids,
    dag=dag,
)
    
<<<<<<< HEAD
t2 = PythonOperator(
    task_id='get_dataset_info', 
    python_callable=get_dataset_info,
    dag=dag,
    op_kwargs={'model_mode':'Auto', 'model_id':1}
)


t3 = PythonOperator(
    task_id='Linear_Regression_Keras', 
    python_callable=linear_regression_sklearn,
    dag=dag,
    op_kwargs={'model_mode':'Auto', 'model_id':2}
)

t4 = PythonOperator(
    task_id='XGBoost_Regressor', 
    python_callable=linear_regression_sklearn,
    dag=dag,
    op_kwargs={'model_mode':'Auto', 'model_id':3}
)


t1 >> [t2,t3,t4]
    


>>>>>>> development

