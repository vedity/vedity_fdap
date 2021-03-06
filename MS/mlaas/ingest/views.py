# -*- coding: utf-8 -*-
# python 2
'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 INFOSENSE          07-DEC-2020           1.0           Intial Version 

 ****************************************************************************************/

*/
'''
# Python library import
import json
import logging
import traceback
import pandas as pd
import datetime 
from rest_framework.views import APIView
from rest_framework.response import Response

# Database variable file import
from database import *

# Ingest utils files
from .utils import ingestion
from .utils.ingestion import *

# Common file imports
from common.utils.exception_handler.python_exception import *
from common.utils.exception_handler.python_exception.common.common_exception import *
from common.utils.exception_handler.python_exception.ingest.ingest_exception import *


from common.utils.json_format.json_formater import *
from common.utils.activity_timeline import *
from common.utils.activity_timeline import activity_timeline
from common.utils.logger_handler import custom_logger as cl
from preprocess.utils.preprocessing import PreprocessingClass
user_name = 'admin'
log_enable = True
LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()
logger = logging.getLogger('ingest_view')


DBObject=db.DBClass() #Get DBClass object
connection,connection_string=DBObject.database_connection(database,user,password,host,port) #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)
IngestionObj=ingestion.IngestClass(database,user,password,host,port) #initialize the Ingest Class 
timeline_Obj=activity_timeline.ActivityTimelineClass(database,user,password,host,port) #initialize the ActivityTimeline Class
json_obj = JsonFormatClass() #initialize the JsonFormat Class 
PC_OBJ = PreprocessingClass(database,user,password,host,port)

# Class for Project to retrive & insert 
#It will take url string as mlaas/ingest/create_project/.
class CreateProjectClass(APIView):

        def get(self, request, format=None):
                """
                This function is used to get Project details uploaded by the user.
        
                Args  : 
                        User_name[(String)]   :[Name of user]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival & insertions failed or successfull),
                        Response(return false if failed otherwise json data)
                """
                try:
                        logging.info("data ingestion : CreateProjectClass : GET Method : execution start")
                        user_name  = request.query_params.get('user_name') #get Username
                        project_df = IngestionObj.show_project_details(user_name,DBObject,connection) #call show_project_details to retrive project detail data and it will return dataframe
                        if isinstance(project_df,str): #check the instance of dataset_df
                                status_code,error_msg=json_obj.get_Status_code(project_df) # extract the status_code and error_msg from project_df
                                logging.info("data ingestion : CreateProjectClass : GET Method : execution : status_code :"+ status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                logging.info("data ingestion : CreateProjectClass : GET Method : execution : status_code : 200")
                                return Response({"status_code":"200","error_msg":"successfull retrival","response":project_df})  

                except Exception as e:
                        logging.error("data ingestion : CreateProjectClass : GET Method : " + str(e))
                        logging.error("data ingestion : CreateProjectClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})  
        
        def post(self, request, format=None):
                """
                This function is used to Create Project and Insert Uploaded CSV File data into Table

                Args  : 
                        User_name[(String)]   :[Name of user]
                        ProjectName[(String)] :[Name of project]
                        Description[(String)] :[Discreption of project]
                        dataset_visibility[(String)] :[Name of Visibility public or private]
                        dataset_id[(Integer)] :[ID of dataset selected by user from dropdown]
                        inputfile(CSV File)   :[Input CSV file]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival & insertions failed or successfull),
                        Response(return false if failed otherwise true)
                """
                try:
                                
                        logging.info("data ingestion : CreateProjectClass : POST Method : execution start")
                        user_name=request.POST.get('user_name')  #get Username
                        project_name=request.POST.get('project_name') #get project_name
                        project_desc=request.POST.get('description') #get project description
                        dataset_desc=request.POST.get('dataset_description') #get dataset description
                        dataset_name = request.POST.get('dataset_name')#get dataset name
                        page_name = "Create Project"
                        dataset_visibility = request.POST.get('visibility') #get Visibility
                        dataset_id = request.POST.get('dataset_id') # get dataset_id, if selected the dataset from dropdown menu otherwise it will be blank 
                        file_name = None
                        if dataset_id == "":
                                dataset_id = None
        
                        if dataset_id == None :
                                exists_project_status = IngestionObj.does_project_exists(project_name,user_name,DBObject,connection) 
                                if exists_project_status == False:
                                        file=request.FILES['inputfile'] #get inputfile Name
                                        try:
                                                file_data = pd.read_csv(request.FILES['inputfile']) # read the csv file and store into dataframe variable
                                        except:
                                                return Response({"status_code":500,"error_msg":"Invalid CSV Format, Please upload UTF-8 encoded CSV","response":"false"})
                                        file_check_status = IngestionObj.check_file(file,file_data) # call check_file function to verify csv file data
                                        if file_check_status !=True: #if file_check_status not equal to true then file must  be inappropriate
                                                status_code,error_msg=json_obj.get_Status_code(file_check_status) # extract the status_code and error_msg from file_check_status
                                                logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                                        file_path="static/server/" 
                                        file_name = IngestionObj.save_file(DBObject,connection,user_name,dataset_visibility,file,file_path) 
                                                 
                                else:
                                        return Response({"status_code":"500","error_msg":"Project already exist","response":"false"})
                        
                                                
                        datasetexist_status=IngestionObj.does_dataset_exists(dataset_name,user_name,DBObject,connection) #get the status if dataset exist or not 
                        if datasetexist_status != False:
                                status_code,error_msg=json_obj.get_Status_code(datasetexist_status) # extract the status_code and error_msg from datasetexist_status
                                logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :200")
                                project_Status,project_id,dataset_id=IngestionObj.create_project(project_name,project_desc,page_name,DBObject,connection,dataset_desc,dataset_name,dataset_visibility,file_name,dataset_id,user_name)    #call create_project method to create project and insert csv data into table
                                if project_Status != 0:
                                        status_code,error_msg=json_obj.get_Status_code(project_Status) # extract the status_code and error_msg from project_Status
                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                                else:
                                        activity_id = 'in_3'
                                        activity_df = timeline_Obj.get_activity(activity_id,"US")
                                        activity_description = "{x} '{y}'".format(x=activity_df[0]["activity_description"],y= project_name)
                                        end_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                                        activity_status,index = timeline_Obj.insert_user_activity(activity_id,user_name,project_id,dataset_id,activity_description,end_time)
                                        if isinstance(activity_status,str):
                                                status_code,error_msg=json_obj.get_Status_code(activity_status) # extract the status_code and error_msg from activity_status
                                                logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                                        else:
                                                logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code : 200")
                                                return Response({"status_code":"200","status_msg":"Successfully Inserted","response":"true"}) 

                except Exception as e:
                        logging.error("data ingestion : CreateProjectClass : POST Method : " + str(e))
                        logging.error("data ingestion : CreateProjectClass : POST Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})      


# Class for Dataset to retrive & insert
# It will take url string as mlaas/ingest/create_dataset/.    
class CreateDatasetClass(APIView):
        
        # permission_classes = [IsAuthenticated]
        def get(self, request, format=None):
                """
                This function is used to Create Dataset and Insert Uploaded CSV File data into Table.
                

                Args   :
                        user_name[(String)]   :[Name of user]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival & insertions failed or successfull),
                        Response(return false if failed otherwise json data) 
                """
                try:
                        logging.info("data ingestion : CreateDatasetClass : GET Method : execution start")
                        user_name=request.query_params.get('user_name')  #get Username
                        dataset_df=IngestionObj.show_dataset_details(user_name,DBObject,connection) #Call show_dataset_details method it will return dataset detail for specific user_name
                        if isinstance(dataset_df,str): #check the instance of dataset_df
                                status_code,error_msg=json_obj.get_Status_code(dataset_df) # extract the status_code and error_msg from dataset_df
                                logging.info("data ingestion : CreateDatasetClass : GET Method : execution stop : status_code : "+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                logging.info("data ingestion : CreateDatasetClass : GET Method : execution stop : status_code : 200")
                                return Response({"status_code":"200","error_msg":"successfull retrival","response":dataset_df})  #return Data             
                except Exception as e:
                        logging.error("data ingestion : CreateDatasetClass : GET Method : " + str(e))
                        logging.error("data ingestion : CreateDatasetClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})  
        
        def post(self, request, format=None):
                """
                This function is used to Create Dataset and Insert Uploaded CSV File data into Table.

                Args   :
                        user_name[(String)]   :[Name of user]
                        dataset_Name[(String)] :[Name of dataset]
                        dataset_visibility[(String)] :[Name of Visibility public or private]
                        inputfile(CSV File)   :[Input CSV file]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival & insertions failed or successfull),
                        Response(return false if failed otherwise true) 
                """
                try: 
                        logging.info("data ingestion : CreateDatasetClass : POST Method : execution start")
                        user_name=str(request.POST.get('user_name'))  #get Username
                        dataset_name=request.POST.get('dataset_name') #get dataset name
                        dataset_visibility= request.POST.get('visibility') #get the visibility
                        dataset_desc = request.POST.get('dataset_description') #get the description
                        page_name = "Create dataset"
                        exists_dataset_status=IngestionObj.does_dataset_exists(dataset_name,user_name,DBObject,connection) #call does_dataset_exists, check if dataset name exist for that perticular user name return false if not,otherwise true
                        if exists_dataset_status == False:
                                file=request.FILES['inputfile'] #get inputfile Name
                                

                                try:
                                        file_data = pd.read_csv(request.FILES['inputfile'])   # read the csv file and store into dataframe variable 
                                
                                except:
                                        return Response({"status_code":500,"error_msg":"Invalid CSV Format, Please upload UTF-8 encoded CSV","response":"false"})
                                                
                                                                        
                                file_check_status = IngestionObj.check_file(file,file_data)  # call check_file function to verify csv file data
                                        
                                if file_check_status !=True:
                                        status_code,error_msg=json_obj.get_Status_code(file_check_status) # extract the status_code and error_msg from file_check_status
                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+error_msg)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})

                                file_path="static/server/" #server path where all the dataset will store
                                file_name =IngestionObj.save_file(DBObject,connection,user_name,dataset_visibility,file,file_path)
                        else:
                                return Response({"status_code":"500","error_msg":"Dataset name exists","response":"false"})

                        dataset_Status,dataset_id=IngestionObj.create_dataset(dataset_name,file_name,dataset_visibility,user_name,dataset_desc,page_name,DBObject,connection,connection_string) #call create_dataset method to create dataset and insert csv data into table
                        if dataset_Status != 0:
                                status_code,error_msg=json_obj.get_Status_code(dataset_Status) # extract the status_code and error_msg from dataset_status
                                logging.info("data ingestion : CreateDatasetClass : POST Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                activity_id = 'in_1'
                                activity_df = timeline_Obj.get_activity(activity_id,"US")
                                activity_description = "{x} '{y}'".format(x=activity_df[0]["activity_description"],y= dataset_name)
                                
                                project_id=0
                                end_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                                activity_status,index = timeline_Obj.insert_user_activity(activity_id,user_name,project_id,str(dataset_id),activity_description,end_time)
                                if isinstance(activity_status,str):
                                        status_code,error_msg=json_obj.get_Status_code(activity_status) # extract the status_code and error_msg from activity_status
                                        logging.info("data ingestion : CreateDatasetClass : POST Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                                else:        
                                        logging.info("data ingestion : CreateDatasetClass : POST Method : execution stop : status_code : 200")
                                        return Response({"status_code":"200","error_msg":"Successfully Inserted","response":"true"})
                        
                except Exception as e:
                                logging.error("data ingestion : CreateDatasetClass : POST Method : Exception : " + str(e))
                                logging.error("data ingestion : CreateDatasetClass : POST Method : "+traceback.format_exc())
                                return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 


#class for retrive csv data 
#It will take url string as mlaas/ingest/data_detail/.
class DataDetailClass(APIView):

        def post(self, request, format=None ):
                """
                this function used to get the fixed length of records with option to search and sorting 

                Args : 
                        start_index[(Integer)] : [value of the starting index]
                        length[(Integer)] :[value of length of records to be shown]
                        sort_type[(String)] : [value of sort_type ascending or descending]
                        sort_index[(Integer)] : [index value of the column to perform sorting]
                        global_value[(String)] : [value that need be search in table]
                        dataset_id[(Integer)] : [Id of the dataset table]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for retrival & insertions failed or successfull),
                        Response(return false if failed otherwise json data)
                """
                data = json.dumps(request.data) #get all the request body parameter
                request_body = json.loads(data) #get all the request body parameter and convert into dictonery
                draw=request_body["draw"]  #get the draw
                try:
                        logging.info("data ingestion : DataDetailClass : POST Method : execution start")
                        start_index=request_body["start"] #get the start index
                        length=request_body["length"] #get the length
                        order_values=request_body['order'] #get the order values
                        sort_type=order_values[0]['dir'] # get the sort type value(asc or desc)
                        sort_index=order_values[0]['column'] # get the sort_index column value
                        global_value=request_body['search']['value']  #get String value for global search
                        customefilter=request_body['customfilter']  #get customfilter values   
                        dataset_id = request.query_params.get('dataset_id') #get dataset_id
                        schema_id = request.query_params.get('schema_id') #get dataset_id
                        if schema_id=="undefined":
                                schema_id=None
                        rowcount=DBObject.get_row_count(connection,dataset_id) #get the row count
                        dataset_df,filtercount=IngestionObj.show_data_details(dataset_id,start_index,length,sort_type,sort_index,global_value,customefilter,schema_id,DBObject,connection) #call show_data_details and it will return dataset detail data in dataframe
                        if isinstance(dataset_df,str): #check the instance of dataset_df
                                status_code,error_msg=json_obj.get_Status_code(dataset_df) # extract the status_code and error_msg  from dataset_df
                                logging.info("data ingestion : DataDetailClass : POST Method : execution stop : status_code :"+status_code)
                                return Response({"draw":draw,"recordsTotal":0,"recordsFiltered":0,"data":[]})  #return Data
                        else:
                                logging.info("data ingestion : DataDetailClass : POST Method : execution stop : status_code :200")
                                return Response({"draw":draw,"recordsTotal":filtercount,"recordsFiltered":filtercount,"data":dataset_df})  #return Data             
                except Exception as e:
                        logging.error("data ingestion : DataDetailClass : GET Method : Exception :" + str(e))
                        logging.error("data ingestion : DataDetailClass : GET Method : " +traceback.format_exc())
                        return Response({"draw":draw,"recordsTotal":0,"recordsFiltered":0,"data":[]})


#class to get column name list of csv data
#It will take url string as mlaas/ingest/data_detail/column_list/
class DataDetailColumnListClass(APIView):
        def get(self, request, format=None):
                """ 
                this function used to get the list of column name from the csv file uploaded by user
                for the specific dataset id
                
                Args:
                        [(dataset_id)] : [Id of the dataset table]
                Return: 
                        [(List)] : [List of column name]

                """
                try:
                        logging.info("data ingestion : DataDetailClass : GET Method : execution start")
                        schema_id = request.query_params.get('schema_id') #get dataset_id
                        dataset_id = request.query_params.get('dataset_id') #get dataset_id
                        logger.info("test"+schema_id)
                        if schema_id !="undefined":
                                column_list=DBObject.get_schema_columnlist(connection,schema_id,type="None") #call show_data_details and it will return dataset detail data in dataframe
                        else:
                                column_list=DBObject.get_column_list(connection,dataset_id) #call show_data_details and it will return dataset detail data in dataframe
                        if isinstance(column_list,str): #check the instance of dataset_df
                                status_code,error_msg=json_obj.get_Status_code(column_list) # extract the status_code and error_msg  from column_list
                                logging.info("data ingestion : DataDetailClass : GET Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                # column_name = DBObject.get_column_name(dataset_df) #Extract column name from dict and return list column name except index column
                                logging.info("data ingestion : DataDetailClass : GET Method : execution stop : status_code :200")
                                getcolumn = json_obj.get_column_name(column_list)
                                return Response({"status_code":"200","error_msg":"successfull retrival","response":getcolumn})  #return Data             
                except Exception as e:
                        logging.error("data ingestion : DataDetailClass : GET Method : Exception :" + str(e))
                        logging.error("data ingestion : DataDetailClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 

#class for delete project
#It will take url string as mlaas/ingest/delete/project_detail/.
class DeleteProjectDetailClass(APIView):  
        def delete(self, request, format=None):
                """
                This function is used to delete project detail.

                Args   : 
                        User_name[(String)]   :[Name of user]
                        project_id[(Integer)] :[ID of project]
                        
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                try:
                        logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution start")
                        user_name=request.query_params.get('user_name') # get username
                        project_id=request.query_params.get('project_id')  #get tablename 
                        
                        cleanup_process = PC_OBJ.get_dag_status(DBObject, connection, project_id) # check cleanup is running
                        if cleanup_process == True:
                                return Response({"status_code":"500","error_msg":"Can't Delete,Cleanup Process is going on!","response":"false"}) 

                        modelling_process = PC_OBJ.get_modelling_status(DBObject,connection,project_id) #check model runnig
                        if modelling_process == True:
                                return Response({"status_code":"500","error_msg":"Can't Delete,Model Running!","response":"false"}) 
                        if cleanup_process == False and modelling_process == False:
                                project_status,dataset_id,project_name= IngestionObj.delete_project_details(project_id,user_name,DBObject,connection)  #get the project_status if project Deletion failed or successfull
                                if project_status != 0:
                                        status_code,error_msg=json_obj.get_Status_code(project_status) # extract the status_code and error_msg from  project_status
                                        logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                                else:
                                        activity_id = 'in_4'
                                        activity_df = timeline_Obj.get_activity(activity_id,"US")
                                        activity_description = "{x} '{y}'".format(x=activity_df[0]["activity_description"],y= project_name)
                                        end_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                                        activity_status,index = timeline_Obj.insert_user_activity(activity_id,user_name,project_id,str(dataset_id),activity_description,end_time)
                                        if isinstance(activity_status,str):
                                                status_code,error_msg=json_obj.get_Status_code(activity_status) # extract the status_code and error_msg from activity_status
                                                logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                                        else:
                                                logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :200")
                                                return Response({"status_code":"200","error_msg":"Successfully deleted","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : DeleteProjectDetailClass : DELETE Method :  Exception : " + str(e))
                        logging.error("data ingestion : DeleteProjectDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 

#class for delete dataset
#It will take url string as mlaas/ingest/delete/dataset_detail/.
class DeleteDatasetDetailClass(APIView):
        def delete(self, request, format=None):
                """
                This function is used to delete Dataset detail.
                It will take url string as mlaas/ingest/delete/dataset_detail/.

                Args   : 
                        User_name[(String)]   :[Name of user]
                        dataset_id[(Integer)] :[ID of dataset]

                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                try:
                        logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution start")
                        user_name=request.query_params.get('user_name') #get user_name
                        dataset_id=request.query_params.get('dataset_id')  #get dataset_name
                        dataset_status,dataset_name=IngestionObj.delete_dataset_detail(dataset_id,user_name,DBObject,connection) #get the dataset_status if dataset Deletion failed or successfull 
                        if dataset_status != 0:
                                status_code,error_msg=json_obj.get_Status_code(dataset_status) # extract the status_code and error_msg from dataset_status
                                logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                
                                project_id=0
                                activity_id = 'in_2'
                                activity_df = timeline_Obj.get_activity(activity_id,"US")
                                activity_description = "{x} '{y}'".format(x=activity_df[0]["activity_description"],y= dataset_name)
                                end_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                                activity_status,index = timeline_Obj.insert_user_activity(activity_id,user_name,project_id,dataset_id,activity_description,end_time)
                                if isinstance(activity_status,str):
                                        status_code,error_msg=json_obj.get_Status_code(activity_status) # extract the status_code and error_msg from activity_status
                                        logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                                else:
                                        logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution stop : status_code :200")
                                        return Response({"status_code":"200","error_msg":"Successfully deleted","response":"true"})

                except Exception as e:
                        logging.error("data ingestion : DeleteDatasetDetailClass : DELETE Method : Exception : " + str(e))
                        logging.error("data ingestion : DeleteDatasetDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 

#class to delete Csv data(data_detail)                     
#It will take url string as mlaas/ingest/delete/data_detail/.

class DeleteDataDetailClass(APIView):
        def delete(self, request, format=None):
                """
                This function is used to delete data(CSV) detail.
                It will take url string as mlaas/ingest/delete/data_detail/.

                Args  : 
                        user_name[(String)]  :  [Name of the user]
                        table_name[(String)] :  [Name of the table]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                try:
                        logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution start")
                        user_name=request.query_params.get('user_name')
                        table_name=request.query_params.get('table_name')  #get tablename
                        data_detail_status=IngestionObj.delete_data_detail(table_name,user_name,DBObject,connection) 
                        if data_detail_status != 0 :
                                status_code,error_msg=json_obj.get_Status_code(data_detail_status) # extract the status_code and error_msg from data_detail_status
                                logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution stop : status_code :200")
                                return Response({"status_code":"200","error_msg":"Successfully deleted","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : DeleteDataDetailClass : DELETE Method : Exception :" + str(e))
                        logging.error("data ingestion : DeleteDataDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 


#class to check Project name exist or not
#It will take url string as mlaas/ingest/project_exist/.
class ProjectExistClass(APIView):
        def get(self,request,format=None):
                """
                This function is used to Check ProjectName already exist or not.

                Args  : 
                        user_name[(String)] : [Name of the user]
                        project_name[(String)] : [Name of the project]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                logging.info("data ingestion : ProjectExistClass : GET Method : execution start")
                user_name = request.query_params.get('user_name') #get user_name
                project_name =request.query_params.get('project_name') #get project_name
                projectexist_status=IngestionObj.does_project_exists(project_name,user_name,DBObject,connection) # get status
                if projectexist_status != False:
                        status_code,error_msg=json_obj.get_Status_code(projectexist_status) # extract the status_code and error_msg from projectexist_status
                        logging.info("data ingestion : ProjectExistClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : ProjectExistClass : GET Method : execution stop : status_code :200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":"true"})  


#class to check dataset name exist or not
#It will take url string as mlaas/ingest/dataset_exist/.
class DatasetExistClass(APIView):
        def get(self,request,format=None):
                """
                This function is used to Check Dataset already exist or not.

                Args  : 
                        user_name[(String)] : [Name of the user]
                        dataset_name[(String)] : [Name of the dataset]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                logging.info("data ingestion : DatasetExistClass : GET Method : execution start")
                user_name = request.query_params.get('user_name') #get user_name
                dataset_name = request.query_params.get('dataset_name') #get dataset_name
                datasetexist_status=IngestionObj.does_dataset_exists(dataset_name,user_name,DBObject,connection) #get the status if dataset exist or not 
                if datasetexist_status != False:
                        status_code,error_msg=json_obj.get_Status_code(datasetexist_status) # extract the status_code and error_msg from datasetexist_status
                        logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":"true"})  

#class to get public dataset name 
#It will take url string as mlaas/ingest/datasetname_exist/.
class DatasetNameClass(APIView):
        def get(self,request,format=None):
                """
                This function is used to get all public dataset of  Dataset name which are uploaded user.

                Args  : 
                        user_name[(String)] : [Name of the user]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                logging.info("data ingestion : DatasetNameClass : GET Method : execution start")
                user_name =request.query_params.get('user_name') #get user_name
                dataset_df=IngestionObj.show_dataset_names(user_name,DBObject,connection) #retrive all dataset name for that perticular user_name
                if isinstance(dataset_df,str): #check the instance of dataset_df
                        status_code,error_msg=json_obj.get_Status_code(dataset_df) # extract the status_code and error_msg from dataset_df
                        logging.info("data ingestion : DatasetNameClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : DatasetNameClass : GET Method : execution stop : status_code : 200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":dataset_df}) 


class ProjectDetailClass(APIView):
        def get(self,request,format=None):
                """
                This function is used to get project detail.

                Args  : 
                        project_id[(String)] : [id of the project]
                Return : 
                        status_code(500 or 200),
                        error_msg(Error message for deletion failed or successfull),
                        Response(false or true)
                """
                logging.info("data ingestion : ProjectExistClass : GET Method : execution start")
                user_name =request.query_params.get('user_name') #get project_name
                project_id =request.query_params.get('project_id') #get project_name
                project_df = IngestionObj.show_project_details(user_name,DBObject,connection,project_id) #call show_project_details to retrive project detail data and it will return dataframe
                if isinstance(project_df,str): #check the instance of dataset_df
                        status_code,error_msg=json_obj.get_Status_code(project_df) # extract the status_code and error_msg from project_df
                        logging.info("data ingestion : CreateProjectClass : GET Method : execution : status_code :"+ status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : CreateProjectClass : GET Method : execution : status_code : 200")
                        return Response({"status_code":"200","error_msg":"successfull retrival","response":project_df})  
                

