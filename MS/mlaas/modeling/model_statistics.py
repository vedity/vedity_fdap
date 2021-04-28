'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
Shivani Bhalodiya      25-JAN-2021           1.0           Initial Version 
Mann Purohit           02-FEB-2021           1.1           Initial Version 

*/
'''

# Imports Necessary Library.
import json
import pandas as pd
import numpy as np
import ast
from database import *
from pandas import DataFrame
import logging
import traceback

# Imports Common Class Files.
from common.utils.logger_handler import custom_logger as cl
from common.utils.exception_handler.python_exception.modeling.modeling_exception import *
from common.utils.exception_handler.python_exception.common.common_exception import *
from common.utils.exception_handler.python_exception.modeling.modeling_exception import *
from common.utils.database import db
from modeling.all_method import CommonMethodClass

# Declare Global Object And Varibles.
user_name = 'admin'
log_enable = True
 
LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()
 
logger = logging.getLogger('view')
DBObject=db.DBClass()     
connection,connection_string=DBObject.database_connection(database,user,password,host,port)      #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)

db_param_dict = {'DBObject':DBObject,'connection':connection,'connection_string':connection_string}
cmobj = CommonMethodClass(db_param_dict)



class ModelStatisticsClass:

    def __init__(self, db_param_dict):
        
        self.DBObject = db_param_dict['DBObject']
        self.connection = db_param_dict['connection']

    
    def learning_curve(self, experiment_id):
        """This function is used to get learning curve of particular experiment.

        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe for learning curve.]
            
        """
        logging.info("modeling : ModelStatisticsClass : learning_curve : Exception Start" )
        str1 = '/learning_curve.json'
        artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)#will get artifact_uri for particular experiment
        json_data = cmobj.get_json(artifact_uri)# will get json data from particular artifact_uri location
        learning_curve_json = cmobj.set_json(json_data,3)#will round json data 
        logging.info("modeling : ModelStatisticsClass : learning_curve : Exception End" )
        return learning_curve_json
    
    def actual_vs_prediction(self,experiment_id,model_type):
        """This function is used to get actuval_vs_prediction of particular experiment.

        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe for actual_vs_prediction.]
            
        """
    
        logging.info("modeling : ModelStatisticsClass : actual_vs_prediction : Exception Start" )
        str1 = '/predictions.json'
        artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)#will get artifact_uri for particular experiment
        json_data = cmobj.get_json(artifact_uri)# will get json data from particular artifact_uri location
        actual_vs_prediction_data = cmobj.set_json(json_data,3)#will round json data    
        actual_vs_prediction_json = cmobj.actual_vs_prediction_fun(experiment_id,model_type,actual_vs_prediction_data)
        logging.info("modeling : ModelStatisticsClass : actual_vs_prediction : Exception End" )
        return actual_vs_prediction_json

    def features_importance(self, experiment_id):
        """This function is used to get features_importance of particular experiment.

        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe for features_importance.]
            
        """
        logging.info("modeling : ModelStatisticsClass : features_importance : Exception Start" )
        str1 = '/features_importance.json'
        artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)#will get artifact_uri for particular experiment
        json_data = cmobj.get_json(artifact_uri)# will get json data from particular artifact_uri location
        features_importance_json = cmobj.set_json(json_data,2)#will round json data    
        logging.info("modeling : ModelStatisticsClass : features_importance : Exception End" )
        return features_importance_json

    def model_summary(self, experiment_id):
        """This function is used to get model_summary of particular experiment.
 
        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]
 
        Returns:
            [data_frame]: [it will return the dataframe for model_summary.]
            
        """
        try:
            logging.info("modeling : ModelStatisticsClass : model_summary : Exception Start" )
            str1 = '/model_summary.json'
            artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)#will get artifact_uri for particular experiment
            model_summary = cmobj.get_json(artifact_uri)# will get json data from particular artifact_uri location

            sql_command = 'select model_desc from mlaas.model_master_tbl mmt, mlaas.model_experiment_tbl met where mmt.model_id=met.model_id and met.experiment_id='+str(experiment_id)
 
            model_desc = self.DBObject.select_records(self.connection, sql_command)
            if model_desc is None:
                raise DatabaseConnectionFailed(500)
 
            elif len(model_desc) == 0: # If the experiment_id is not present in the mlaas.runs.
                raise DataNotFound(500)
            
            model_desc = model_desc.iloc[0, 0]
 
            model_summary.update({'Model_Description': model_desc})
            logging.info("modeling : ModelStatisticsClass : model_summary : Exception End")
            return model_summary
 
        except (DatabaseConnectionFailed,DataNotFound) as exc:
            logging.error("modeling : ModelStatisticsClass : model_summary : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : model_summary : " +traceback.format_exc())
            return exc.msg

    def show_confusion_matrix(self,experiment_id):
            
        """
        This function retuns confusion matrix for classification models

        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe for model_summary.]        
        """

        unscaled_df,target_features = cmobj.get_unscaled_data(experiment_id)
        str1 = '/confusion_matrix.json'
        artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)
        confusion_matrix = cmobj.get_json(artifact_uri)
        confusion_matrix_df = pd.DataFrame(confusion_matrix)
        confusion_matrix_dict = confusion_matrix_df.to_dict()
    
        key = np.unique(unscaled_df[target_features[1:]+'_str']).tolist()
    
        key_val = []

        for value in confusion_matrix_dict.values():
            thislist = []
            for i,j in value.items():
                thislist.append(j)
            key_val.append(thislist)
                  
        confusion_matrix_json = {"key":key,"key_val":key_val}

        return confusion_matrix_json


    def show_roc_curve(self, experiment_id):
        """Returns the scores for the AUC-ROC curve.

        Args:
            experiment_id (int): ID of the experiment.
        """
        logging.info("modeling : ModelStatisticsClass : show_roc_curve : Exception Start" )
        unscaled_df,target_features = cmobj.get_unscaled_data(experiment_id)
        str1 = '/roc_scores.json'
        artifact_uri = cmobj.get_artifact_uri(experiment_id,str1)#will get artifact_uri for particular experiment
        roc_scores = cmobj.get_json(artifact_uri)# will get json data from particular artifact_uri location
        
        classes = np.unique(unscaled_df[target_features[1]+'_str']).tolist()

        final_dict = dict()
        for key in roc_scores.keys():
            data_dict = roc_scores[key]
            new_dict = dict(zip(classes, list(data_dict.values())))
            final_dict[key] = new_dict
        
        final_dict['classes'] = classes
        
        return final_dict



    
    def performance_metrics(self, experiment_id):
        """This function is used to get performance_metrics of particular experiment.

        Args:
            experiment_id ([object]): [Experiment id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe for performance_metrics.]
            
        """
        try:
            logging.info("modeling : ModelStatisticsClass : performance_metrics : Exception Start")
            sql_command = 'select mtr.key, mtr.value, met.experiment_id from mlflow.metrics mtr, mlaas.model_experiment_tbl met where mtr.run_uuid=met.run_uuid and met.experiment_id='+str(experiment_id)
            perform_metrics_df = self.DBObject.select_records(self.connection, sql_command)
            if perform_metrics_df is None:
                raise DatabaseConnectionFailed(500)

            if len(perform_metrics_df) == 0: # If the experiment_id is not present in the mlaas.runs.
                raise DataNotFound(500)

            perform_pivot_df = perform_metrics_df.pivot(columns='key', values='value', index='experiment_id').round(2)
            perform_pivot_df.columns = [name.upper().replace('_', ' ') for name in perform_pivot_df.columns.values]
            sql_command = 'select met.experiment_id, met.exp_created_on as "Created On", mmt.model_name as "Model Name" from mlaas.model_experiment_tbl met, mlaas.model_master_tbl mmt where mmt.model_id=met.model_id and met.experiment_id='+str(experiment_id)
            experiment_df = self.DBObject.select_records(self.connection, sql_command)
            if experiment_df is None:
                raise DatabaseConnectionFailed(500)

            if len(experiment_df) == 0: # If the experiment_id is not present in the mlaas.runs.
                raise DataNotFound(500)

            experiment_df = experiment_df.set_index('experiment_id')
            merged_df = pd.merge(experiment_df, perform_pivot_df, left_index=True, right_index=True)
            final_dict = merged_df.to_dict(orient='records')[0]
            logging.info("modeling : ModelStatisticsClass : performance_metrics : Exception end")
            return {'key': final_dict.keys(), 'value': final_dict.values()}

        except (DatabaseConnectionFailed,DataNotFound) as exc:
            logging.error("modeling : ModelStatisticsClass : performance_metrics : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : performance_metrics : " +traceback.format_exc())
            return exc.msg
        

    def show_running_experiments(self, project_id):
        """This function is used to get experiments_list of particular project.

        Args:
            project_id ([object]): [Project id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe of experiments_list.]
            
        """
        try:
            logging.info("modeling : ModelStatisticsClass : show_running_experiments : Exception Start")
            # Get the necessary values from the mlaas.model_experiment_tbl where the state of the experiment is 'running'.
            sql_command = "select e.name as experiment_name,mv.* from (select met.*,mmt.model_name, mmt.model_type,dt.dataset_name, 0.0 as cv_score, 0.0 as holdout_score"\
                          " from mlaas.model_experiment_tbl met,mlaas.model_master_tbl mmt,mlaas.dataset_tbl dt"\
                          " where met.model_id = mmt.model_id and met.dataset_id=dt.dataset_id and met.project_id="+str(project_id)+" and status='running' )"\
                          " as mv left outer join mlflow.experiments e"\
                          " on mv.experiment_id=e.experiment_id"
                          
            model_experiment_data_df = self.DBObject.select_records(self.connection, sql_command)
            if model_experiment_data_df is None:
                raise DatabaseConnectionFailed(500)

            if len(model_experiment_data_df) == 0:# If there are no experiments for a particular project_id.
                sql_command = ''
                return []
            # Converting final_df to json
            json_data = model_experiment_data_df.to_json(orient='records',date_format='iso')
            final_data = json.loads(json_data)
            logging.info("modeling : ModelStatisticsClass : show_running_experiments : Exception End")
            return final_data
        except (DatabaseConnectionFailed,ModelIsStillInQueue) as exc:
            logging.error("modeling : ModelStatisticsClass : show_running_experiments : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : show_running_experiments : " +traceback.format_exc())
            return exc.msg

    def check_running_experiments(self, project_id):

        try:
            logging.info("modeling : ModelStatisticsClass : check_running_experiments : Exception Start")
            sql_command = "select exp_name from mlaas.model_dags_tbl mdt,dag_run dr where mdt.run_id=dr.run_id"\
                        " and dr.state in ('running') and mdt.project_id={}".format(project_id)
            exp_name = self.DBObject.select_records(self.connection, sql_command)

            if exp_name is None:
                raise DatabaseConnectionFailed(500)

            if len(exp_name) == 0:# If there are no experiments for a particular project_id.
                return {'exp_name': ''}
            
            exp_name = exp_name['exp_name'][0]
            logging.info("modeling : ModelStatisticsClass : check_running_experiments : Exception End")
            return {'exp_name': exp_name}
        except (DatabaseConnectionFailed,ModelIsStillInQueue) as exc:
            logging.error("modeling : ModelStatisticsClass : check_running_experiments : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : check_running_experiments : " +traceback.format_exc())
            return exc.msg


    def show_all_experiments(self, project_id):
        """This function is used to get experiments_list of particular project.

        Args:
            project_id ([object]): [Project id of particular experiment.]

        Returns:
            [data_frame]: [it will return the dataframe of experiments_list.]
            
        """
        try:
            logging.info("modeling : ModelStatisticsClass : show_all_experiments : Exception Start")
            # Get everything from model_experiment_tbl and, experiment name, model_name and dataset_name associated with a particular project_id.
            sql_command = "select met.*,e.name as experiment_name,mmt.model_name, mmt.model_type,dt.dataset_name,"\
                          "round(cast(sv.cv_score as numeric),3) as cv_score,round(cast(sv.holdout_score as numeric),3) as holdout_score "\
                          " from mlaas.model_experiment_tbl met,mlaas.model_master_tbl mmt,mlaas.score_view sv,mlaas.dataset_tbl dt,mlflow.experiments e"\
                          " where met.model_id = mmt.model_id and met.experiment_id=sv.experiment_id and met.dataset_id=dt.dataset_id and met.experiment_id=e.experiment_id "\
                          " and met.project_id="+str(project_id)+" order by met.exp_created_on desc"
                          
            model_experiment_data_df = self.DBObject.select_records(self.connection, sql_command)

            if model_experiment_data_df is None:
                raise DatabaseConnectionFailed(500)

            if len(model_experiment_data_df) == 0:# If there are no experiments for a particular project_id.
                return []
            # Converting final_df to json
            json_data = model_experiment_data_df.to_json(orient='records',date_format='iso')
            final_data = json.loads(json_data)
            logging.info("modeling : ModelStatisticsClass : show_all_experiments : Exception End")
            return final_data
        except (DatabaseConnectionFailed,DataNotFound) as exc:
            logging.error("modeling : ModelStatisticsClass : show_all_experiments : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : show_all_experiments : " +traceback.format_exc())
            return exc.msg
        
        
    def check_model_status(self,project_id,experiment_name):
        """This function is used to check the 'state' of the given experiment.

        Args:
            project_id (int): project_id
            experiment_name (string): experiment's name

        Raises:
            DatabaseConnectionFailed: If the connection is not established with the Database.
            DataNotFound: If there is no data in the database for a particular query.

        Returns:
            [string]: state of the experiment
        """
        
        try:
            logging.info("modeling : ModelStatisticsClass : check_model_status : Exception Start")
            # Get dag_id and run_id from the model_dags_tbl with associated experiment_name.
            sql_command ="select dag_id,run_id from mlaas.model_dags_tbl where project_id="+str(project_id)+" and exp_name='"+experiment_name+"'"
            
            dag_df = self.DBObject.select_records(self.connection, sql_command)

            if dag_df is None:
                raise DatabaseConnectionFailed(500)

            if len(dag_df) == 0 :
                return 0
            
            dag_id,run_id = dag_df['dag_id'][0],dag_df['run_id'][0]
            
            # Get the state of the experiment associated with run_id.
            sql_command = "select state from dag_run where dag_id='"+dag_id+"' and run_id='"+run_id +"'"
            state_df = self.DBObject.select_records(self.connection, sql_command)
            
            if state_df is None:
                raise DatabaseConnectionFailed(500)

            if len(state_df) == 0 :
                raise DataNotFound(500)

            # Update Project Status 
            status = state_df['state'][0]
            if status == 'running':
                st=0
            elif status == 'success':
                sql_command = "select status from mlaas.model_experiment_tbl where dag_run_id='"+run_id+"' and status='failed'" #will get status from experiment table.
                exp_state_df = self.DBObject.select_records(self.connection, sql_command)
                if exp_state_df is None:
                    raise DatabaseConnectionFailed(500)
                
                if len(exp_state_df) == 0:
                    st=1
                else:
                    st=2         
            else:
                st=2
            
            # Update the model_status in the project table.
            sql_command = "update mlaas.project_tbl set model_status="+str(st)+" where project_id="+str(project_id)
            project_upd_status = self.DBObject.update_records(self.connection,sql_command)
            #status=state_df['state'][0]
            logging.info("modeling : ModelStatisticsClass : check_model_status : Exception End")
            return st
        
        except (DatabaseConnectionFailed,DataNotFound) as exc:
            logging.error("modeling : ModelStatisticsClass : check_model_status : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : check_model_status : " +traceback.format_exc())
            return exc.msg
    

    def check_existing_experiment(self,project_id, experiment_name):
        """Checks if the experiment_name entered by the user already exists in a particular project id or not.

        Args:
            experiment_name ([string]): User entered experiment name.

        Raises:
            ExperimentAlreadyExist: [This experiment already exist, so enter a new,unique experiment name.]

        Returns:
            integer: status code of the experiment_name exists.
        """
        try:
            logging.info("modeling : ModelStatisticsClass : check_existing_experiment : Exception Start")
            # Get the experiment's name from the model_dag_tbl
            sql_command="select * from mlaas.model_dags_tbl where exp_name='"+experiment_name+"' and project_id="+str(project_id)# will get all information for particular experiment
            experiment_data_df = self.DBObject.select_records(self.connection, sql_command)

            if experiment_data_df is None: # If the database connection fails.
                return 0
            elif len(experiment_data_df) > 0: # If the experiment name already exists.
                raise ExperimentAlreadyExist(500)
            else:
                return 0
    
        except (ExperimentAlreadyExist) as exc:
            logging.error("modeling : ModelStatisticsClass : check_existing_experiment : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : check_existing_experiment : " +traceback.format_exc())
            return exc.msg

        
    def compare_experiments_grid(self, experiment_ids):
        """This function is called when user wants to compare multiple experiments.

        Args:
            experiment_ids ([tuple]): It contains all the experiment ids.

        Raises:
            DatabaseConnectionFailed: If the database connection is not established.
            DataNotFound: If the entry for the query is not found in the database.

        Returns:
            Dictionary: It contains the accuracy_metrics, model_name, model_params, and the associated experiment_id.
        """
            # Get the model parameters for the associated experiment_ids.
        try:
            logging.info("modeling : ModelStatisticsClass : compare_experiments_grid : Exception Start")
            exp_ids = tuple(experiment_ids)
            sql_command = 'select prms.key, prms.value, met.experiment_id from mlflow.params prms,mlaas.model_experiment_tbl met where prms.run_uuid=met.run_uuid and met.experiment_id in'+str(exp_ids)
            params_df = self.DBObject.select_records(self.connection, sql_command)
            if params_df is None:
                raise DatabaseConnectionFailed(500)

            if len(params_df) == 0 :
                raise DataNotFound(500)
            # Rearraging Dataframe according to our requirement.
            params_pivot_df = params_df.pivot(index='experiment_id', columns='key', values='value')
            
            # Get the accuracy metrics for the associated experiment_ids.
            sql_command = 'select mtr.key, mtr.value, met.experiment_id from mlflow.metrics mtr,mlaas.model_experiment_tbl met where mtr.run_uuid=met.run_uuid and met.experiment_id in'+str(exp_ids)
            metrics_df = self.DBObject.select_records(self.connection, sql_command)
            if metrics_df is None:
                raise DatabaseConnectionFailed(500)

            if len(metrics_df) == 0 :
                raise DataNotFound(500)
            # Rearraging Dataframe according to our requirement.
            metrics_pivot_df = metrics_df.pivot(index='experiment_id', columns='key', values='value')
            
            
            # Get the model_name for the associated experiment_ids.
            sql_command = 'select mmt.model_name, met.experiment_id from mlaas.model_master_tbl mmt, mlaas.model_experiment_tbl met where mmt.model_id=met.model_id and met.experiment_id in '+str(exp_ids)
            model_names_df = self.DBObject.select_records(self.connection, sql_command)
            if model_names_df is None:
                raise DatabaseConnectionFailed(500)

            if len(model_names_df) == 0 :
                raise DataNotFound(500)
            
            model_names_df = model_names_df.set_index('experiment_id') # Set index to experiment_id

            metrics_params_df = metrics_pivot_df.merge(params_pivot_df, left_index=True, right_index=True)

            final_df = model_names_df.merge(metrics_params_df, left_index=True, right_index=True)
            
            sql_command = "select name from mlflow.experiments where experiment_id in "+str(experiment_ids)
                        #   " and met.experiment_id in "+str(exp_ids)

            exp_names = tuple(self.DBObject.select_records(self.connection, sql_command)['name'])

            final_df['experiment_name'] = exp_names
            columns = final_df.columns.values

            logging.info("COLUMN NAMES:-       -------------"+str(columns))
            logging.info("RESPONSE DATA:-       -------------"+str(final_df.to_dict(orient='records')))
            # logging.info("COLUMN NAMES:-       -------------"+str(columns))

            logging.info("modeling : ModelStatisticsClass : compare_experiments_grid : Exception End")
            return {'column_names': columns, 'responsedata': final_df.to_dict(orient='records')}

        except (ExperimentAlreadyExist) as exc:
            logging.error("modeling : ModelStatisticsClass : compare_experiments_grid : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : compare_experiments_grid : " +traceback.format_exc())
            return exc.msg


    def compare_experiments_graph(self, experiment_ids):
        try:
            logging.info("modeling : ModelStatisticsClass : compare_experiments_graph : Exception Start")
            sql_command = "SELECT model_type from mlaas.model_experiment_tbl met, mlaas.model_master_tbl mmt where met.model_id = mmt.model_id and met.experiment_id in"+str(experiment_ids)
            model_types_df = self.DBObject.select_records(self.connection, sql_command)
            if model_types_df is None:
                raise DatabaseConnectionFailed(500)

            if len(model_types_df) == 0 :
                raise DataNotFound(500)

            model_types = tuple(model_types_df['model_type'])
            sql_command = "select name from mlflow.experiments where experiment_id in "+str(experiment_ids)
            experiment_names_df = self.DBObject.select_records(self.connection, sql_command)
            
            if experiment_names_df is None:
                raise DatabaseConnectionFailed(500)

            if len(experiment_names_df) == 0 :
                raise DataNotFound(500)
            
            experiment_names = list(experiment_names_df['name'])

            actual_vs_prediction_json = self.actual_vs_prediction(experiment_ids[0], model_types[0])

            if model_types[0] == 'Regression':
                actual_vs_prediction_df = pd.DataFrame(actual_vs_prediction_json)
                index = actual_vs_prediction_df['index'].tolist()
                predicted_column = actual_vs_prediction_df.filter(regex=('.*_prediction.*')).columns.values[0]
                actual_column = predicted_column.replace('_prediction', '')
                actual = actual_vs_prediction_df[actual_column].tolist()
                predicted_list = []
                predicted_list.append({'exp_name': experiment_names[0],'values': actual_vs_prediction_df[predicted_column].tolist()})

                for i in range(len(experiment_ids) - 1):
                    predicted_list.append({'exp_name': experiment_names[i+1],'values': self.actual_vs_prediction(experiment_ids[i+1], model_types[i+1])[predicted_column]})

                comparision_dict = {'index': index, 'actual': actual, 'predicted': predicted_list,'model_type':'Regression'}
                
                return comparision_dict

            elif model_types[0] == 'Classification':
                # actual_vs_prediction_json = {"keys":key,"actual":actual_lst,"prediction":prediction_lst}
                keys = actual_vs_prediction_json['keys']
                actual = actual_vs_prediction_json['actual']
                
                predicted_list = []
                predicted_list.append({'exp_name': experiment_names[0],'values': actual_vs_prediction_json['prediction']})

                for i in range(len(experiment_ids) - 1):
                    predicted_list.append({'exp_name': experiment_names[i+1],'values': self.actual_vs_prediction(experiment_ids[i+1], model_types[i+1])['prediction']})

                comparision_dict = {'key': keys, 'actual': actual, 'predicted': predicted_list,'model_type':'Classification'}
                logging.info("modeling : ModelStatisticsClass : compare_experiments_graph : Exception Start")
                return comparision_dict
        except (ExperimentAlreadyExist) as exc:
            logging.error("modeling : ModelStatisticsClass : compare_experiments_graph : Exception " + str(exc))
            logging.error("modeling : ModelStatisticsClass : compare_experiments_graph : " +traceback.format_exc())
            return exc.msg

        
