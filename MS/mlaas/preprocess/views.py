'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Nisha Barad          12-JAN-2021           1.0         Intial Version 

 ****************************************************************************************/

*/
'''

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils.Exploration import dataset_exploration
from .utils import preprocessing
from common.utils.database import db
from database import *
from common.utils.json_format.json_formater import *
from database import *
import json
import pandas as pd
import logging




# user_name = 'admin'
# log_enable = False

# LogObject = cl.LogClass(user_name,log_enable)
# LogObject.log_setting()

# #logger = logging.getLogger('view')

DBObject=db.DBClass()     #Get DBClass object
connection,connection_string=DBObject.database_connection(database,user,password,host,port)      #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)
ExploreObj =  preprocessing.PreprocessingClass(database,user,password,host,port)


class DatasetExplorationClass(APIView):
    
    def get(self,request,format=None):
        """
        This class is used to get the data statistics for each of the feature in the table.
        It will take url string as mlaas/preprocess/exploredata/get_data_statistics.

        Args  : 
                DatasetId[(Integer)]   :[Dataset ID]
                
        Return : 
                status_code(500 or 200),
                error_msg(Error message for retrival failed or successfull),
                Response(return false if failed otherwise json data)
        """

        try:
            dataset_id = request.query_params.get('dataset_id') #get datasetid       
            statics_df =  ExploreObj.get_exploration_data(dataset_id) #pass datasetid in function
            if isinstance(statics_df,str): #check the instance of statics_df
                status_code,error_msg=get_Status_code(statics_df) # extract the status_code and error_msg from statics_df
                logging.info("data preprocessing : DatasetExplorationClass : GET Method : execution : status_code :"+ status_code)
                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
            else:
                table_df = statics_df.to_json(orient='records')
                table_df = json.loads(table_df)
                return Response({"status_code":"200","error_msg":"successfull retrival","response":table_df})
        except Exception as e:
            return Response({"status_code":"500","error_msg":str(e),"response":"false"})

