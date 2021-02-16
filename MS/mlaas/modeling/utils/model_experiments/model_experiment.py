'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Vipul Prajapati      25-JAN-2021           1.0           Initial Version 
 
*/
'''


# import pandas as pd
from .db import DBClass
import json
from pandas import DataFrame

class ExperimentClass:
    
    def __init__(self,experiment_id,experiment_name,run_uuid,project_id,dataset_id,
                user_id,model_id,model_mode,DBObject, connection,connection_string):
        
        self.run_uuid = run_uuid
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.model_id = model_id
        self.model_mode = model_mode
        
       
          
    def add_experiments(self, DBObject, connection, connection_string):
        
        table_name='mlaas.model_experiment_tbl'
        cols = 'experiment_id,run_uuid,project_id ,dataset_id,user_id,model_id,model_mode' 
        
        row = self.experiment_id,self.run_uuid,self.project_id ,self.dataset_id,self.user_id,self.model_id,self.model_mode    
        row_tuples = [tuple(row)]
        
        experiment_status = DBObject.insert_records(connection,table_name,row_tuples,cols)
        
        return experiment_status
           
            
    # def learning_curve(self, experiment_id, DBObject, connection):
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select artifact_uri from runs where experiment_id='+str(experiment_id)
    #     artifact_uri = DBObject.select_records(connection, sql_command).iloc[0,0]
    #     learning_curve_uri = artifact_uri + '/learning_curve.json'
    #     json_data = open(learning_curve_uri, 'r')
    #     learning_curve = json_data.read()
    #     return learning_curve



    # def actual_vs_prediction(self, experiment_id, DBObject, connection):
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select artifact_uri from runs where experiment_id='+str(experiment_id)
    #     artifact_uri = DBObject.select_records(connection, sql_command).iloc[0,0]
    #     actual_vs_prediction_uri = artifact_uri + '/predictions.json'
    #     json_data = open(actual_vs_prediction_uri, 'r')
    #     actual_vs_prediction = json_data.read()
    #     return actual_vs_prediction

    
    # def features_importance(self, experiment_id, DBObject, connection):
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select artifact_uri from runs where experiment_id='+str(experiment_id)
    #     artifact_uri = DBObject.select_records(connection, sql_command).iloc[0,0]
    #     features_importance_uri = artifact_uri + '/features_importance.json'
    #     json_data = open(features_importance_uri, 'r')
    #     features_importance = json_data.read()
    #     return features_importance

    
    # def model_summary(self, experiment_id, DBObject, connection):
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select artifact_uri from runs where experiment_id='+str(experiment_id)
    #     artifact_uri = DBObject.select_records(connection, sql_command).iloc[0,0]
    #     model_summary_uri = artifact_uri + '/model_summary.json'
    #     json_data = open(model_summary_uri, 'r')
    #     model_summary = json_data.read()
    #     return model_summary
    
    # def performance_metrics(self, experiment_id, DBObject, connection): # Remaining
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select run_uuid from runs where experiment_id='+str(experiment_id)
    #     run_uuid = DBObject.select_records(connection, sql_command).iloc[0, 0]
        
    #     sql_command = "select key, value from metrics where run_uuid='"+str(run_uuid) +"'"
    #     metrics_df = DBObject.select_records(connection, sql_command).set_index('key') 
    #     metrics_df.index.name = None
    #     metrics_json = metrics_df.iloc[:, 0].to_json()
        
    #     return metrics_json



    def accuracy_metrics(self, experiment_id, DBObject, connection):
        
        sql_command = 'select run_uuid from runs where experiment_id='+str(experiment_id)
        run_uuid = DBObject.select_records(connection, sql_command).iloc[0, 0]
        
        sql_command = "select key,value from metrics where run_uuid='"+str(run_uuid)+"' and (key='cv_score' or key='holdout_score')"
        accuracy_df = DBObject.select_records(connection, sql_command).set_index('key') 
        return accuracy_df
    
    def show_model_details(self, experiment_id, DBObject, connection):
        sql_command = 'select ms.model_id,ms.model_name,ms.model_desc,exp.experiment_id from mlaas.model_experiment_tbl exp,mlaas.model_master_tbl ms where exp.model_id = ms.model_id and exp.experiment_id ='+str(experiment_id)
        model_details_df = DBObject.select_records(connection, sql_command)
        
        accuracy_df = self.accuracy_metrics(experiment_id, DBObject, connection)
        
        model_details_json = model_details_df.to_json()
        accuracy_json = accuracy_df.to_json()
       
        return model_details_json,accuracy_json







    # def get_hyperparameters_values(self, experiment_id, DBObject, connection):
    #     # DbObject,connection,connection_string = self.get_db_connection()
    #     sql_command = 'select run_uuid from runs where experiment_id='+experiment_id
    #     run_uuid = DBObject.select_records(connection, sql_command).iloc[0, 0]

    #     sql_command = 'select key, value from params where run_uuid='+run_uuid
    #     hyperparameters = DBObject.select_records(connection, sql_command)
    #     hyperparameters_json = hyperparameters.set_index('key')['value'].to_json()
    #     return hyperparameters_json
    