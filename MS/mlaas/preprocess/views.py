'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Nisha Barad          12-JAN-2021           1.0         Intial Version 

 ****************************************************************************************/

*/
'''
import json
import pandas as pd
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from .utils.Exploration import dataset_exploration
from .utils import preprocessing

from .utils.schema.schema_creation import *
from common.utils.json_format.json_formater import *
from common.utils.database import db
from database import *

#from .utils.Visual import data_visualization
# from .utils import data_visualization as dv

user_name = 'admin'
log_enable = False

LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()
logger = logging.getLogger('preprocess_view')

DBObject=db.DBClass() #Get DBClass object
connection,connection_string=DBObject.database_connection(database,user,password,host,port) #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)
ExploreObj =  preprocessing.PreprocessingClass(database,user,password,host,port) #initialize Preprocess class object


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
            logging.info("data preprocess : DatasetExplorationClass : GET Method : execution start")
            dataset_id = request.query_params.get('dataset_id') #get datasetid     
            schema_id =request.query_params.get('schema_id') #get the schema id  
            statics_df =  ExploreObj.get_exploration_data(dataset_id,schema_id) #pass datasetid in function
            
            if isinstance(statics_df,str): #check the instance of statics_df
                status_code,error_msg=json_obj.get_Status_code(statics_df) # extract the status_code and error_msg from statics_df
                logging.info("data preprocessing : DatasetExplorationClass : GET Method : execution : status_code :"+ status_code)
                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
            else:
                stats_df = statics_df.to_json(orient='records')
                stats_df = json.loads(stats_df)
                logging.info("data preprocess : DatasetExplorationClass : GET Method : execution start: status code : 200")
                return Response({"status_code":"200","error_msg":"successfull retrival","response":stats_df})
        except Exception as e:
            return Response({"status_code":"500","error_msg":str(e),"response":"false"})

# class DataVisualizationClass(APIView):
                            
#     def get(self,request,format=None):
#         try:
#             graph = request.query_params.get('graph')
#             datasetid = request.query_params.get('dataset_id')
#             column_name = request.query_params.get('column_name')
#             visual_df = dv.VisualizationClass(database,user,password,host,port)
#             if graph == 'histogram':
#                 visual_df = visual_df.get_hist_visualization(DBObject,connection,datasetid,column_name)
#             elif graph == 'countplot':
#                 visual_df =visual_df.get_countplot_visualization(DBObject,connection,datasetid,column_name)
#             elif graph == 'boxplot':
#                 visual_df =visual_df.get_boxplot_visualization(DBObject,connection,datasetid,column_name)
#             return Response({"status_code":"200","error_msg":"successfull retrival","response":visual_df}) 
#         except Exception as e:
#            return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 



class SchemaSaveClass(APIView):

        def post(self,request,format=None):
                """ 
                Args :
                        Request_Body[(String)] : [list of dictonery in form of string]
                        dataset_id [(Integer)]  : [Id of the dataset table]
                        project_id [(Integer)]  : [Id of the project table]
                        schema_id [(Integer)]  : [Id of the schema table]
                Return :
                        status_code(500 or 200),
                        error_msg(Error message for insertions failed or successfull),
                        Response(return false if failed otherwise true) 
                        
                """
                try:
                        logging.info("data preprocess : SchemaSaveClass : POST Method : execution start")

                        update_schema_data=json.loads(request.body) #convert the data into dictonery
                        schema_data = update_schema_data["data"] #access "data" key value from the schema_data dict
                        schema_id = request.query_params.get('schema_id') #get the schema id
                        dataset_id = request.query_params.get('dataset_id') #get the dataset id
                        project_id = request.query_params.get('project_id') #get the project id
                        
                        schema_status=ExploreObj.save_schema_data(schema_data,project_id,dataset_id,schema_id)

                        if isinstance(schema_status,str): #check the instance of dataset_df
                                status_code,error_msg=json_obj.get_Status_code(schema_status) # extract the status_code and error_msg from schema_status
                                logging.info("data preprocess : SchemaSaveClass : POST Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                logging.info("data preprocess : SchemaSaveClass : POST Method : execution stop : status_code :200")
                                return Response({"status_code":"200","error_msg":"Successfully save","response":"true"})           
                except Exception as e:
                        logging.error("data preprocess : SchemaSaveClass : POST Method : Exception :" + str(e))
                        logging.error("data preprocess : SchemaSaveClass : POST Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})
                        






# Class to retrive & insert for Schema data
# It will take url string as mlaas/ingest/dataset_schema/. 
class SchemaClass(APIView):
        
        def get(self,request,format=None):
                """
                this function used to get the column datatype,attribute type,column name and change_column_name for schema page from csv dataset uploaded by the user.

                Args : 
                        dataset_id [(Integer)]  : [Id of the dataset table]
                        project_id [(Integer)]  : [Id of the project table]

                Return :
                        status_code(500 or 200),
                        error_msg(Error message for retrival failed or successfull),
                        Response(return false if failed otherwise json data) 
                """
                try:
                        logging.info("data preprocess : DatasetSchemaClass : GET Method : execution start")
                        
                        schema_id=request.query_params.get('schema_id') #get schema id
                        
                        #get the schema detail,if exist then return data else return string with error_msg and status code
                        schema_data=ExploreObj.get_schema_details(schema_id) 
                        if isinstance(schema_data,list):  
                                logging.info("data preprocess : DatasetSchemaClass : GET Method : execution stop")
                                return Response({"status_code":"200","error_msg":"Successfull retrival","response":schema_data})
                        else:
                                status_code,error_msg=json_obj.get_Status_code(schema_data) # extract the status_code and error_msg from schema_data
                                logging.info("data preprocess : DatasetSchemaClass : GET Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                except Exception as e:
                        logging.error("data preprocess : DataDetailClass : GET Method : Exception :" + str(e))
                        logging.error("data preprocess : DataDetailClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})
                            

class ScheamColumnListClass(APIView):

        def get(self, request, format=None):
                """
                This class is used to get  schema column list.
                It will take url string as mlaas/dataset_schema/column_attribute_list/.

                Args  : 
                        
                        
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival failed or successfull),
                        Response(return false if failed otherwise json data)
       
                this function used to get Attribute list for schema page and

                Return:
                        status_code(500 or 200),
                        error_msg(Error message for retrive successfull or unsuccessfull),
                        Response(return false if failed otherwise List of column attribute)  
                """
                try :
                                logging.info("data preprocess : ScheamAttributeListClass : POST Method : execution start")
                                column_attribute = {"column_attribute":["Ignore","Target","Select"] }
                                return Response({"status_code":"200","error_msg":"Successfull retrival","response":column_attribute})
                except Exception as e:
                                logging.error("data preprocess : ScheamAttributeListClass : POST Method : Exception :" + str(e))
                                logging.error("data preprocess : ScheamAttributeListClass : POST Method : "+ traceback.format_exc())
                                return Response({"status_code":"500","error_msg":"Failed","response":str(e)})