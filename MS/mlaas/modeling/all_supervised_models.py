'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Vipul Prajapati      25-JAN-2021           1.0         Initial Version 
 Mann Purohit         02-FEB-2021           1.1         Initial Version

*/
'''

# All Necessary Imports
import pandas as pd
import numpy as np
import json
import ast 
import logging
import traceback
import mlflow
import mlflow.sklearn
import uuid 
import logging
import sys
import os
from database import *
from common.utils.database import db

# Regression Class File Imports
from modeling.utils.model_utils.sklearn_regression.linear_regression import *
from modeling.utils.model_utils.sklearn_regression.ridge_regression import *
from modeling.utils.model_utils.sklearn_regression.lasso_regression import *
from modeling.utils.model_utils.sklearn_regression.elasticnet_regression import *
from modeling.utils.model_utils.sklearn_regression.kneighbors_regression import *
from modeling.utils.model_utils.sklearn_regression.decisiontree_regression import *
from modeling.utils.model_utils.sklearn_regression.randomforest_regression import *
from modeling.utils.model_utils.sklearn_regression.gradientboost_regression import *
from modeling.utils.model_utils.sklearn_regression.xgboost_regression import *
# from modeling.utils.model_utils.keras_regression.linear_regression_keras import *

# Classification Class File Imports
from modeling.utils.model_utils.sklearn_classification.logistic_regression import *
from modeling.utils.model_utils.sklearn_classification.kneighbors_classification import *
from modeling.utils.model_utils.sklearn_classification.svm_classification import *
from modeling.utils.model_utils.sklearn_classification.decisiontree_classification import *
from modeling.utils.model_utils.sklearn_classification.naive_bayes_classification import *
from modeling.utils.model_utils.sklearn_classification.randomforest_classification import *
from modeling.utils.model_utils.sklearn_classification.gradientboost_classification import *
from modeling.utils.model_utils.sklearn_classification.xgboost_classification import *
# from modeling.utils.model_utils.keras_classification.logistic_regression_keras import *

# Common Class File Imports
from modeling.utils.model_experiments import model_experiment
from modeling.split_data import SplitData
from common.utils.logger_handler import custom_logger as cl
from common.utils.exception_handler.python_exception.modeling.modeling_exception import *
from common.utils.dynamic_dag import dag_utils as du

# Global Variables And Objects
user_name = 'admin'
log_enable = True
LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()
logger = logging.getLogger('model_identifier')

# Declare Database Object
DBObject=db.DBClass()     
connection,connection_string=DBObject.database_connection(database,user,password,host,port) 

# Declare Experiment Object
ExpObject = model_experiment.ExperimentClass(DBObject, connection, connection_string) 

#Declaring dag object
DAG_OBJ = du.DagUtilsClass()

def get_supervised_models(model_type):
    """This function is used to get all supervised model based on model type (Regression or Classification).

    Args:
        model_type ([string]): [it is the type of model, either regression or classification]

    Returns:
        [dict]: [it will return all models of passed model type.]
    """
    
    # This Query Select model_id,model_name,model_class_name,model_hyperparams from the model master table.
    sql_command = "select mmt.model_id,mmt.model_name,mmt.model_class_name,amp.hyperparam as model_hyperparams,mmt.algorithm_type from mlaas.model_master_tbl mmt,mlaas.auto_model_params amp "\
                  "where mmt.model_id=amp.model_id and mmt.model_type='"+ model_type +"' order by model_id"
    
    # Get Model DataFrame              
    model_df = DBObject.select_records(connection,sql_command)
    # Get All Model Dictionary.
    model_dict = model_df.to_dict(orient="list")

    return model_dict



def get_model_data(user_id, project_id, dataset_id):
    """This function is used to get all data related to execute models. 

    Args:
        user_id ([integer]): [unique id of the user.]
        project_id ([integer]): [unique id of the project.]
        dataset_id ([integer]): [unique id of the dataset.]

    Returns:
        [list,list,array,dict]: [it will return input and target features list and all splits array of train and test data]
    """
    
    # Get Scaled Split Dictionary.
    scaled_split_dict = SplitData().get_scaled_split_dict(DBObject,connection,project_id, dataset_id)
    
    # Get Splits Numpy Array Of Train Test And Valid Datasets.
    X_train,X_valid,X_test,y_train,y_valid,y_test = SplitData().get_split_datasets(scaled_split_dict)
    
    # Get Input And Target Features List.
    input_features_list, target_features_list = SplitData().get_features_list(user_id, project_id, dataset_id, DBObject, connection)

    try:
        classes = SplitData().get_original_classes(scaled_split_dict)
        logging.info("CLASSSSSSEEEEEESSSSSSSSSSSSSSSSSSSSS--------------------------------------****************"+str(classes))
    except:
        classes = []
    scaled_split_dict['classes'] = classes

    return input_features_list, target_features_list, X_train, X_test, X_valid, y_train, y_test, y_valid, scaled_split_dict



def start_pipeline(dag,run_id,execution_date,ds,**kwargs):
    """This Function is used to start modeling pipeline.

    Args:
        dag ([object]): [object of the dag.]
        run_id ([string]): [run id of the dag.]
        execution_date ([timestamp]): [dag execution date.]
        ds ([object]): [dag start date]
    """
    # Get Model's Basic Parameter. 
    basic_params_dict = ast.literal_eval(kwargs['dag_run'].conf['basic_params_dict'])

    
    dag_id = dag.dag_id
    
    project_id = int(basic_params_dict['project_id'])
    dataset_id = int(basic_params_dict['dataset_id'])
    user_id = int(basic_params_dict['user_id'])
    exp_name  = basic_params_dict['experiment_name']

    model_mode = basic_params_dict['model_mode']
    model_type = basic_params_dict['model_type']
    algorithm_type = basic_params_dict['algorithm_type']

    table_name='mlaas.model_dags_tbl'
    # Update current running dag information into external model_dag_tbl.
    sql_command = "UPDATE "+table_name+" SET dag_id='"+dag_id+"', run_id='"+run_id+"', execution_date='"+str(execution_date)+"'"\
                  " WHERE project_id="+str(project_id)+" and exp_name='"+exp_name+"'"
    
    update_status = DBObject.update_records(connection, sql_command)
    

    table_name = 'mlaas.model_experiment_tbl'
    cols = 'project_id,dataset_id,user_id,model_id,model_mode,dag_run_id'
    
    # Check Whether Model is running into auto or manual mode.
    if model_mode.lower() == 'auto' :
        
        # This sql command get model ids from model master table for passed model type and algorithm type.
        if algorithm_type.lower() == 'binary':
            # This sql command get model ids from model master table for passed model type and algorithm type.
            sql_command = "select model_id from mlaas.model_master_tbl where model_type='"+ model_type +"'"\
                          " and ( algorithm_type='" + algorithm_type + "' or algorithm_type='Multi')"
        else:
            # This sql command get model ids from model master table for passed model type and algorithm type.
            sql_command = "select model_id from mlaas.model_master_tbl where model_type='"+ model_type +"'"\
                          " and algorithm_type='" + algorithm_type + "'"
                    
        # Get Model Id DataFrame.
        model_df = DBObject.select_records(connection,sql_command)
        # Get Model Ids.
        model_ids = model_df['model_id'].to_list()
            
    else:
        # Get Model's Master Dict. In case of manual modeling.
        master_dict = ast.literal_eval(kwargs['dag_run'].conf['master_dict'])
        # Get Model Ids.
        model_ids = master_dict['model_id']
      
    # This loop insert all model id into model experiment table.  
    for model_id in model_ids:
        
        row = project_id,dataset_id ,user_id,model_id,model_mode,run_id
        row_tuples = [tuple(row)]
        exp_status = DBObject.insert_records(connection,table_name,row_tuples,cols)

        
         
 
def supervised_models(run_id,**kwargs):
    """This function is used to run all supervised models.

    Args:
        run_id ([string ]): [run id of the currently running dag.]
    """
    check_flag = 'top'
    
    try:
        # This will set mlflow tracking uri which will help us to store all parameters into database. 
        mlflow.set_tracking_uri("postgresql+psycopg2://{}:{}@{}:{}/{}?options=-csearch_path%3Ddbo,mlflow".format(user, password, host, port, database))
        
        # Get Basis Model's Parameters.
        basic_params_dict = ast.literal_eval(kwargs['dag_run'].conf['basic_params_dict'])
        
        project_id = int(basic_params_dict['project_id'])
        dataset_id = int(basic_params_dict['dataset_id'])
        user_id = int(basic_params_dict['user_id'])
        
        model_mode = basic_params_dict['model_mode']
        model_type = basic_params_dict['model_type']
        algorithm_type = basic_params_dict['algorithm_type']
        experiment_name  = basic_params_dict['experiment_name']
            
        # Get Input,Target Features List And ALl numpy array of train test and valid datasets and also scaled splits parameters dict.
        input_features_list, target_features_list, X_train, X_test, X_valid, y_train, y_test, y_valid, scaled_split_dict = get_model_data(user_id, project_id, dataset_id)
        
        model_id = kwargs['model_id']
        model_name = kwargs['model_name']
        model_class_name = kwargs['model_class_name']
        hyperparameters = kwargs['model_hyperparams']  
        
        hyperparameters['model_name'] = model_name
 
        if model_type.lower() != 'classification':
            scaled_split_dict['classes'] = []
            logging.info("NOT A CLASSIFICATION MODEL. .. CLASSSESS:-  "+str(scaled_split_dict['classes']))


        check_flag = 'outside'
        dag_run_id = run_id
        # Check Running Model Wheather It is Binary Or Multi Class Problem.     
        if algorithm_type == kwargs['algorithm_type'] or algorithm_type.lower() == 'binary':
            
            experiment, experiment_id = ExpObject.get_mlflow_experiment(experiment_name)
            # mlflow set_experiment and run the model.
            with mlflow.start_run(experiment_id=experiment_id) as run:
               
                # Get experiment id and run id from the experiment set.
                run_uuid = run.info.run_id
                experiment_id = experiment.experiment_id
                # Add experiment.
                add_exp_status = ExpObject.add_experiments(experiment_id,experiment_name,run_uuid,
                                                            project_id,dataset_id,user_id,
                                                            model_id,model_mode,dag_run_id)
            
                # Declare CLass File Object.
                LRObject = eval(model_class_name)(input_features_list, target_features_list,
                                                    X_train, X_valid, X_test, y_train, y_valid, y_test,
                                                    scaled_split_dict,hyperparameters)
                
                
                check_flag = 'inside'
                try:
                    # Run model pipeline.
                    LRObject.run_pipeline()
                    # Update Model Status.
                    upd_exp_status = ExpObject.update_experiment('success',check_flag,dag_run_id,experiment_id)
                    
                except ModelFailed as mf:
                    
                    upd_exp_status = ExpObject.update_experiment('failed',check_flag,dag_run_id,experiment_id)
                    failed_reason=traceback.format_exc().splitlines()
                    model_failed_reason_dict= {'main reason': mf.msg,'failed_reason':failed_reason}
                    mlflow.log_dict(model_failed_reason_dict,'model_failed_reason.json')
                    
                    raise ModelFailed(mf.status_code)
                 
    except:
        
        if check_flag == 'outside':
            upd_exp_status = ExpObject.update_experiment('Failed',check_flag,dag_run_id,model_id)
        else:
            upd_exp_status = ExpObject.update_experiment('Failed',check_flag,dag_run_id)
            
        raise ModelFailed(100)
            
            
def end_pipeline(dag_index,**kwargs):
    '''
        To release the dag status
    '''
    #? Releasing the dag
    status = DAG_OBJ.release_dag(connection, index = dag_index)
   
    return status


            
        
        
        
        
        
        
    