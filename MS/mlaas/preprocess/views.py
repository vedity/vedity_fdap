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
from common.utils.database import db
from database import *
import json


# user_name = 'admin'
# log_enable = False

# LogObject = cl.LogClass(user_name,log_enable)
# LogObject.log_setting()

# #logger = logging.getLogger('view')

DBObject=db.DBClass()     #Get DBClass object
connection,connection_string=DBObject.database_connection(database,user,password,host,port)      #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)



class DatasetStatisticsClass(APIView):
    """
        This class is used to show the data statistics for each of the feature in the table.
        It will take url string as mlaas/preprocess/exploredata/get_data_statistics.

        Args  : 
                TableName[(String)]   :[Name of table]
                
        Return : 
                status_code(500 or 200),
                error_msg(Error message for retrival failed or successfull),
                Response(return false if failed otherwise json data)
        """

    def get(self,request,format=None):
        try:
            datasetid = request.query_params.get('dataset_id') #get tablename 
            exploreobj = dataset_exploration.ExploreClass() #python class object 
            table_df = exploreobj.get_dataset_statistics(DBObject,connection,datasetid)  #calls the get_dataset_statisctics python class method and returns dataframe
            table_df = table_df.to_json(orient='records')
            table_df = json.loads(table_df)
            return Response({"status_code":"200","error_msg":"successfull retrival","response":table_df})
        except Exception as e:
            return Response({"status_code":"500","error_msg":str(e),"response":"false"})


class DataVisualizationColumnClass(APIView):
    """
        This class is used to show the columns in the table for boxplot visualization.
        It will take url string as mlaas/preprocess/exploredata/get_column.
        
        Args  : 
                TableName[(String)]   :[Name of table]
                ColumnName[(String)]  :[Name of Columns]
                
        Return : 
                status_code(500 or 200),
                error_msg(Error message for retrival failed or successfull),
                Response(return false if failed otherwise json data)
        """

    def get(self,request,format=None):
        try:
            columnname = request.query_params.get('column_name')  #get columnname
            tablename = request.query_params.get('table_name')  #get tablename
            exploreobj = dataset_exploration.ExploreClass()  #python class object
            column_df = exploreobj.return_columns(DBObject, connection, tablename,columnname)   #calls the return_column python class method and returns dataframe
            return Response({"status_code":"200","error_msg":"successfull retrival","response":column_df})
        except Exception as e:
            return Response({"status_code":"500","error_msg":str(e),"response":"false"})

