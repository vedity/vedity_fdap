'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Jay Shukla         17-Jan-2021           1.0           Created Class
 
*/
'''

#* Library Imports
import logging
import traceback
import pandas as pd

#* Relative Imports
from . import duplicate_data_handling as ddh
from . import feature_scaling as fs
from . import categorical_encoding as ce
from . import math_functions as mf
from . import feature_engineering as fe

#* Commong Utilities
from common.utils.database import db
from common.utils.logger_handler import custom_logger as cl
from common.utils.activity_timeline import activity_timeline
from database import *


#* Defining Logger
user_name = 'admin'
log_enable = True

LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()

logger = logging.getLogger('transformation')



class TransformationClass(ddh.RemoveDuplicateRecordClass, fs.FeaturnScalingClass, ce.EncodeClass, mf.MathOperationsClass, fe.FeatureEngineeringClass):
    '''
        Handles orchastration of the transforamtion related Functions.
    '''
    
    def __init__(self):
        # self.op_diff = 8
        self.AT = activity_timeline.ActivityTimelineClass(database, user, password, host, port)
    
    #* RESCALING
    
    def standard_scaling(self, dataframe):
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution start")
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution stop")
        
        return super().standard_scaling(dataframe)
    
    def min_max_scaling(self, dataframe):
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution start")
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution stop")
        
        return super().min_max_scaling(dataframe)
    
    def robust_scaling(self, dataframe):
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution start")
        
        logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution stop")
        
        return super().robust_scaling(dataframe)
    
    
    # def custom_scaling(self, dataframe, max, min):
        
    #     logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution start")
        
    #     logging.info("data preprocessing : TransformationClass : duplicate_data_removal : execution stop")
        
    #     return super().custom_scaling(dataframe, max, min)
    
    #* Categorical Encoding
    
    # def label_encoding(self, dataframe, col):
    #     '''
    #         Operation id: 27
    #     '''
        
    #     logging.info("data preprocessing : TransformationClass : label_encoding : execution start")
        
    #     cols = [dataframe.columns[i] for i in col]
        
    #     for column in cols:
    #         try:
    #             dataframe[column] =super().label_encoding(dataframe[column])
    #         except:
    #             continue

    #     logging.info("data preprocessing : TransformationClass : label_encoding : execution stop")
    #     return dataframe
    def delete_duplicate_records(self,DBObject,connection,project_id,column_list,old_column_list, table_name, **kwargs):
        '''
            Operation id: ?
        '''
        
        logging.info("data preprocessing : TransformationClass : delete_duplicate_records : execution start")
        try:
            
            col_string = ''
            # operation_id = 7
            for x in old_column_list:
                col_string += '"'+str(x)+'",'
    
            status = super().delete_duplicate_records(DBObject,connection,table_name,col_string[:-1])
                
        except Exception as exc:
            logging.error("data preprocessing : TransformationClass : delete_duplicate_records : Exception "+str(exc))
            logging.error("data preprocessing : TransformationClass : delete_duplicate_records : " +traceback.format_exc())
            
            return 1
        logging.info("data preprocessing : TransformationClass : delete_duplicate_records : execution stop")
        return status
    
    def delete_duplicate_column(self,DBObject,connection,schema_id,project_id, table_name):
        '''
            Operation id: ?
        '''
        
        logging.info("data preprocessing : TransformationClass : delete_duplicate_column : execution start")
        try:
            # #Insert the activity for the operation
            # activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

            status,column_list = super().delete_duplicate_column(DBObject,connection,schema_id,table_name)

            # if status==0:
            #     #Update the activity status for the operation performed
            #     at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)
            return status
        except Exception as exc:
            logging.error("data preprocessing : TransformationClass : delete_duplicate_column : Exception : "+str(exc))
            logging.error("data preprocessing : TransformationClass : delete_duplicate_column : " +traceback.format_exc())
            
            return 1

        

    def delete_low_variance_column(self,DBObject,connection,project_id,schema_id,column_list,old_column_list, table_name,variance=0.5, **kwargs):
        '''
            Operation id: ?
        '''
        
        logging.info("data preprocessing : TransformationClass : delete_low_variance_column : execution start")
        try:

            #Initialize the empty list
            variance_column = []
            status = 0

            for index,col_name in enumerate(old_column_list):

                #Query to get Boolean value  "True" if column variance is less ten te given variance else return "False"
                sql_command = f'''select  case when VARIANCE("{col_name}") < {str(variance)} then 'True' else 'False' end as variance_status from {table_name}  '''
                
                #Execute the sql query
                dataframe = DBObject.select_records(connection,sql_command)
                if str(dataframe['variance_status'][0]) =='True':

                    #Append Name of column into a list variable called "variance_column"
                    variance_column.append(column_list[index])

                    #Delete the column from the table
                    status = super().delete_column(DBObject,connection,schema_id,table_name,col_name)
                
        except Exception as exc:
                logging.error("data preprocessing : TransformationClass : delete_low_variance_column : Exception : "+str(exc))
                logging.error("data preprocessing : TransformationClass : delete_low_variance_column : " +traceback.format_exc())
                return 1

        logging.info("data preprocessing : TransformationClass : delete_low_variance_column : execution stop")
        return status
    


    def label_encoding(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, **kwargs):
        '''
            Operation id: 27
        '''
        #Operation Id to get activity details
        operation_id = 'dp_261'

        logging.info("data preprocessing : TransformationClass : label_encoding : execution start" + str(col))

        index = column_list[0]
        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = super().label_encoding(DBObject, connection, [index,old_cols[i]], table_name)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)
                
            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : label_encoding : execution stop")
        return status

    def one_hot_encoding(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, schema_id, **kwargs):
        '''
            Operation id: 28
        '''
        
        logging.info("data preprocessing : TransformationClass : one_hot_encoding : execution start")
        index = column_list[0]

        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        #Operation Id to get activity details
        operation_id = 'dp_271'

        for i,col_name in enumerate(cols):
            try:

                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = super().one_hot_encoding(DBObject, connection, [index,old_cols[i]], table_name, schema_id)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)
                
            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : one_hot_encoding : execution stop")
        return status

    # def one_hot_encoding(self, dataframe, col):
    #     '''
    #         Operation id: 28
    #     '''
        
    #     logging.info("data preprocessing : TransformationClass : one_hot_encoding : execution start")
        
    #     cols = [dataframe.columns[i] for i in col]
        
    #     for column in cols:
    #         try:
    #             temp_df =super().one_hot_encoding(dataframe[column])
    #             dataframe.drop([column], axis=1, inplace = True)
    #             dataframe = dataframe.join(temp_df)
    #         except:
    #             continue

    #     logging.info("data preprocessing : TransformationClass : one_hot_encoding : execution stop")
    #     return dataframe
    
    #* MATH OPERATIONS
    
    def add_to_column(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, value, **kwargs):
        '''
            Operation id: 29
        '''
        logging.info("data preprocessing : TransformationClass : add_to_column : execution start")
        
        #Operation Id to get activity details
        operation_id = 'dp_281'

        operation = '+'
        
        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = self.perform_math_operation(DBObject, connection, table_name, old_cols[i], operation, value)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)

            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : add_to_column : execution stop")
        return status
    
    def subtract_from_column(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, value, **kwargs):
        '''
            Operation id: 30
        '''
        logging.info("data preprocessing : TransformationClass : subtract_from_column : execution start")
        #Operation Id to get activity details
        operation_id = 'dp_291'

        operation = '-'
        
        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = self.perform_math_operation(DBObject, connection, table_name, old_cols[i], operation, value)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)
            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : subtract_from_column : execution stop")
        return status
    
    def multiply_column(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, value, **kwargs):
        '''
            Operation id: 31
        '''
        logging.info("data preprocessing : TransformationClass : multiply_column : execution start")
        
        operation = '*'
        #Operation Id to get activity details
        operation_id = 'dp_311'

        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = self.perform_math_operation(DBObject, connection, table_name, old_cols[i], operation, value)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)

            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : multiply_column : execution stop")
        return status
    
    def divide_column(self, DBObject,connection,project_id,column_list,old_column_list, table_name, col, value, **kwargs):
        '''
            Operation id: 32
        '''
        logging.info("data preprocessing : TransformationClass : divide_column : execution start")
        
        operation = '/'
        #Operation Id to get activity details
        operation_id = 'dp_301'

        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = self.perform_math_operation(DBObject, connection, table_name, old_cols[i], operation, value)

                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)

            except Exception as exc:
                return exc

        logging.info("data preprocessing : TransformationClass : divide_column : execution stop")
        return status
    
    def split_date_column(self, DBObject, connection, project_id, column_list,old_column_list, table_name, col, **kwargs):
        '''
            Operation id: 321
        '''
        logging.info("data preprocessing : TransformationClass : split_date_column : execution start")
    
        operation_id = 'dp_321'
        
        cols = [column_list[i] for i in col]
        old_cols = [old_column_list[i] for i in col]
        
        for i,col_name in enumerate(cols):
            try:
                #Insert the activity for the operation
                activity_id = self.operation_start(DBObject, connection, operation_id, project_id, col_name)

                status = self.datetime_fe(DBObject, connection, old_cols[i], table_name)
                
                #Update the activity status for the operation performed
                at_status = self.operation_end(DBObject, connection, activity_id, operation_id, col_name)

            except Exception as exc:
                return exc
    
        logging.info("data preprocessing : TransformationClass : split_date_column : execution stop")
        return status
    
    #* ACTIVITY TIMELINE FUNCTIONS
    
    def get_act_desc(self, DBObject, connection, operation_id, col_name, code = 1):
        '''
            Used to get preprocess activity description from the activity master table.
        
            Returns:
            --------
            description (`String`): Description for the activity.
        '''
        logging.info("data preprocessing : TransformationClass : get_activity_desc : execution start")
        
        #? Getting Description
        sql_command = f"select replace (amt.activity_name || ' ' || amt.activity_description, '*', '{col_name}') as description from mlaas.activity_master_tbl amt where amt.activity_id = '{operation_id}' and amt.code = '{code}'"
        
        desc_df = DBObject.select_records(connection,sql_command)
        if not isinstance(desc_df, pd.DataFrame):
            return "Failed to Extract Activity Description."
        
        #? Fatching the description
        description = desc_df['description'].tolist()[0]
        
        logging.info("data preprocessing : TransformationClass : get_activity_desc : execution stop")
        
        return description
            
    def operation_start(self, DBObject, connection, operation_id, project_id, col_name):
        '''
            Used to Insert Activity in the Activity Timeline Table.
            
            Returns:
            --------
            activity_id (`Intiger`): index of the activity in the activity transection table.
        '''
        logging.info("data preprocessing : TransformationClass : operation_start : execution start")
            
        #? Transforming the operation_id to the operation id stored in the activity timeline table. 
        # operation_id += self.op_diff
        
        #? Getting Activity Description
        desc = self.get_act_desc(DBObject, connection, operation_id, col_name, code = 1)
        
        #? Getting Dataset_id & User_Name
        sql_command = f"select pt.dataset_id,pt.user_name from mlaas.project_tbl pt  where pt.project_id = '{project_id}'"
        details_df = DBObject.select_records(connection,sql_command) 
        dataset_id,user_name = int(details_df['dataset_id'][0]),details_df['user_name'][0]
        
        #? Inserting the activity in the activity_detail_table
        _,activity_id = self.AT.insert_user_activity(operation_id,user_name,project_id,dataset_id,desc,column_id =col_name)
        
        logging.info("data preprocessing : TransformationClass : operation_start : execution stop")
        
        return activity_id
    
    def operation_end(self, DBObject, connection, activity_id, operation_id, col_name):
        '''
            Used to update Activity description when the Activity ends.
            
            Returns:
            --------
            status (`Intiger`): Status of the updation.
        '''
        
        logging.info("data preprocessing : TransformationClass : operation_end : execution start")
        
        #? Transforming the operation_id to the operation id stored in the activity timeline table. 
        # operation_id += self.op_diff
        
        #? Getting Activity Description
        desc = self.get_act(DBObject, connection, operation_id, col_name, code = 2)
        
        #? Changing the activity description in the activity detail table 
        status = self.AT.update_activity(activity_id,desc)
        
        logging.info("data preprocessing : TransformationClass : operation_end : execution stop")
        
        return status
    