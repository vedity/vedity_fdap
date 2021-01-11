'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 INFOSENSE          07-DEC-2020           1.0           Intial Version 

 ****************************************************************************************/

*/
'''

import os
import json
import logging
import datetime
import traceback
import pandas as pd
from database import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage
from .utils.schema_creation import *
from .utils import ingestion
from .utils.dataset import dataset_creation
from .utils.ingestion import *
from .utils.api_functionality import *
from common.utils.exception_handler.python_exception.common.common_exception import *
from common.utils.exception_handler.python_exception.ingest.ingest_exception import *
from .utils.project import project_creation
from common.utils.logger_handler import custom_logger as cl
from common.utils.exception_handler.python_exception import *
from common.utils.json_format.json_formater import *

user_name = 'admin'
log_enable = True

LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()

logger = logging.getLogger('view')

DBObject=db.DBClass()     #Get DBClass object
connection,connection_string=DBObject.database_connection(database,user,password,host,port)      #Create Connection with postgres Database which will return connection object,conection_string(For Data Retrival)
IngestionObj=ingestion.IngestClass(database,user,password,host,port)


class UserLoginClass(APIView):
        """ this class used to add user data into table.

        Args   :
                user_name[(String)] : [Name of user]
                password [(String)] : [password value]
        Return :
                status_code(500 or 200),
                error_msg(Error message for login successfull & unsuccessfull),
                Response(return false if failed otherwise true)
        """
        def get(self,request,format=None):
                try:
                        logging.info("data ingestion : UserLoginClass : GET Method : execution start")
                        user_name = request.query_params.get('user_name')
                        password = request.query_params.get('password')
                        user_status = IngestionObj.user_authentication(DBObject,connection,user_name,password)
                        if user_status != True:
                                status_code,error_msg=get_Status_code(user_status)
                                logging.info("data ingestion : UserLoginClass : GET Method : execution : status_code :"+ status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else: 
                                logging.info("data ingestion : UserLoginClass : POST Method : execution stop : status_code : 200")
                                return Response({"status_code":"200","error_msg":"Login Successfull","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : UserLoginClass : GET Method : Exception :" + str(e))
                        logging.error("data ingestion : UserLoginClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"})
        
        def post(self,request):
                try:
                        logging.info("data ingestion : UserLoginClass : POST Method : execution start")
                        user_df=DBObject.read_data('ingest/user_registration_tbl.csv')
                        status=DBObject.load_csv_into_db(connection_string,'user_auth_tbl',user_df,'mlaas')
                        return Response({"Status":status})
                except Exception as e:
                        logging.error("data ingestion : UserLoginClass : POST Method : Exception :" + str(e))
                        logging.error("data ingestion : UserLoginClass : POST Method : " +traceback.format_exc())
                        return Response({"Exception":str(e)}) 

class CreateProjectClass(APIView):
        """
        This class is used to Create Project and Insert Uploaded CSV File data into Table.
        It will take url string as mlaas/ingest/create_project/.
        And if Method is "POST" then it will return Status or if Method is "GET" then it will return Data in Json Format else it will return Method is not allowed.

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
                Response(return false if failed otherwise json data)
        """
        # permission_classes = [IsAuthenticated]
        def get(self, request, format=None):
                try:
                        logging.info("data ingestion : CreateProjectClass : GET Method : execution start")
                        #user_name = request.user.get_username()
                        user_name  = request.query_params.get('user_name') #get Username
                        project_df = IngestionObj.show_project_details(user_name) #call show_project_details to retrive project detail data and it will return dataframe
                        if isinstance(project_df,str): #check the instance of dataset_df
                                status_code,error_msg=get_Status_code(project_df) # extract the status_code and error_msg from project_df
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
                        try:
                                
                                logging.info("data ingestion : CreateProjectClass : POST Method : execution start")
                                # user_name=request.user.get_username()  #get Username
                                user_name=request.POST.get('user_name')  #get Username
                                project_name=request.POST.get('project_name') #get project_name
                                project_desc=request.POST.get('description') #get description
                                dataset_name = request.POST.get('dataset_name')#get dataset name
                                dataset_visibility = request.POST.get('visibility') #get Visibility
                                dataset_id = request.POST.get('dataset_id') # get dataset_id, if selected the dataset from dropdown menu otherwise None 
                                file_name = None
                                if dataset_id == "":
                                        dataset_id = None
                                else:
                                        dataset_id = dataset_id               
                                if dataset_id == None :
                                        exists_project_status = IngestionObj.does_project_exists(project_name,user_name) 
                                        if exists_project_status == False:
                                                file=request.FILES['inputfile'] #get inputfile Name
                                                file_data = pd.read_csv(request.FILES['inputfile'])  
                                                file_check_status = IngestionObj.check_file(file,file_data)
                                                if file_check_status !=True:
                                                        status_code,error_msg=get_Status_code(file_check_status) # extract the status_code and error_msg from file_check_status
                                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                                                file_name = save_file(user_name,dataset_visibility,file,path="static/server/")
                                                 
                                        else:
                                                return Response({"status_code":"500","error_msg":"Project ALready Exist","response":"false"})
                                else:
                                        dataset_id = int(dataset_id)
                                                
                                
                                project_Status=IngestionObj.create_project(project_name,project_desc,dataset_name,dataset_visibility,file_name,dataset_id,user_name)    #call create_project method to create project and insert csv data into table
                                if project_Status != 0:
                                        status_code,error_msg=get_Status_code(project_Status) # extract the status_code and error_msg from project_Status
                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                                else:
                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code : 200")
                                        return Response({"status_code":"200","status_msg":"Successfully Inserted","response":"true"}) 

                        except Exception as e:
                                logging.error("data ingestion : CreateProjectClass : POST Method : " + str(e))
                                logging.error("data ingestion : CreateProjectClass : POST Method : " +traceback.format_exc())
                                return Response({"status_code":"500","error_msg":str(e),"response":"false"})      

        
class CreateDatasetClass(APIView):
        """
        This Class is used to Create Dataset and Insert Uploaded CSV File data into Table.
        It will take url string as mlaas/ingest/create_dataset/.
        And if Method is "POST" then it will return Status or if Method is "GET" then it will return Data in Json Format else it will return Method is not allowed.

        Args   :
                user_name[(String)]   :[Name of user]
                dataset_Name[(String)] :[Name of dataset]
                dataset_visibility[(String)] :[Name of Visibility public or private]
                inputfile(CSV File)   :[Input CSV file]
        Return : 
                status_code(500 or 200),
                error_msg(Error message for retrival & insertions failed or successfull),
                Response(return false if failed otherwise json data) 
        """
        # permission_classes = [IsAuthenticated]
        def get(self, request, format=None):
                try:
                        logging.info("data ingestion : CreateDatasetClass : GET Method : execution start")
                        user_name=request.query_params.get('user_name')  #get Username
                        dataset_df=IngestionObj.show_dataset_details(user_name) #Call show_dataset_details method it will return dataset detail for sepecific user_name
                        if isinstance(dataset_df,str): #check the instance of dataset_df
                                status_code,error_msg=get_Status_code(dataset_df) # extract the status_code and error_msg from dataset_df
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
                try: 
                        logging.info("data ingestion : CreateDatasetClass : POST Method : execution start")
                        # user_name=request.user.get_username()
                        user_name=str(request.POST.get('user_name'))  #get Username
                        dataset_name=request.POST.get('dataset_name') #get dataset name
                        dataset_visibility= request.POST.get('visibility')
                        exists_dataset_status=IngestionObj.does_dataset_exists(dataset_name,user_name) 
                        if exists_dataset_status == False:
                                file=request.FILES['inputfile'] #get inputfile Name
                                file_data = pd.read_csv(request.FILES['inputfile'])                                
                                file_check_status = IngestionObj.check_file(file,file_data)
                                if file_check_status !=True:
                                        status_code,error_msg=get_Status_code(file_check_status) # extract the status_code and error_msg from file_check_status
                                        logging.info("data ingestion : CreateProjectClass : POST Method : execution stop : status_code :"+status_code)
                                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                                file_name = save_file(user_name,dataset_visibility,file,path="static/server/")
                        else:
                                return Response({"status_code":"500","error_msg":"Dataset Name already Exists","response":"false"})

                        dataset_Status=IngestionObj.create_dataset(dataset_name,file_name,dataset_visibility,user_name) #call create_dataset method to create dataset and insert csv data into table
                        if dataset_Status != 0:
                                status_code,error_msg=get_Status_code(dataset_Status) # extract the status_code and error_msg from dataset_status
                                logging.info("data ingestion : CreateDatasetClass : POST Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                logging.info("data ingestion : CreateDatasetClass : POST Method : execution stop : status_code : 200")
                                return Response({"status_code":"200","error_msg":"Successfully Inserted","response":"true"})
                        
                except Exception as e:
                        logging.error("data ingestion : CreateDatasetClass : POST Method : Exception : " + str(e))
			# logging.error("data ingestion : CreateDatasetClass : POST Method : "+traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 
                  
# class DatasetSchemaClass(APIView):
#         def get(self,request,format=None):
#                 dataset_id=request.query_params.get('dataset_id')
#                 schema_obj=SchemaClass(database,user,password,host,port)
#                 schema_data=schema_obj.get_dataset_schema(str(dataset_id))
#                 return Response({"Schema":str(schema_data)})    

#         def put(self,request,format=None):
#                 update_schema_data=json.loads(request.body)

                # user_name=request.POST.get('user_name')
                # dataset_id=request.POST.get('dataset_id')

                # column_list=[]
                # col_attribute_list=[]
                # col_datatype_list=[]
                # column_list.append(request.POST.get('id'))
                # column_list.append(request.POST.get('name'))
                # column_list.append(request.POST.get('sal'))

                # col_attribute_list.append(request.POST.get('datatype_id'))
                # col_attribute_list.append(request.POST.get('datatype_name'))
                # col_attribute_list.append(request.POST.get('datatype_sal'))

                # col_datatype_list.append(request.POST.get('col_id'))
                # col_datatype_list.append(request.POST.get('col_name'))
                # col_datatype_list.append(request.POST.get('col_sal'))

                # schema_obj=SchemaClass(database,user,password,host,port)
                # schema_status=schema_obj.update_dataset_schema(column_list,col_datatype_list,col_attribute_list,dataset_id,user_name)

                return Response({"Status":update_schema_data})           
                

class DataDetailClass(APIView):
        """
        This class is used to Retrive dataset detail Data(CSV Data).
        It will take url string as mlaas/ingest/data_detail/.

        Args  :
                dataset_id[(Integer)] :[ID of dataset]

        Return : 
                status_code(500 or 200),
                error_msg(Error message for retrival failed or successfull),
                Response(return false if failed otherwise json data)
        """   
        # permission_classes = [IsAuthenticated]
        def get(self, request, format=None):
                try:
                        logging.info("data ingestion : DataDetailClass : GET Method : execution start")
                        dataset_id = request.query_params.get('dataset_id') #get dataset_id
                        dataset_df=IngestionObj.show_data_details(dataset_id) #call show_data_details and it will return dataset detail data in dataframe
                        if isinstance(dataset_df,str): #check the instance of dataset_df
                                status_code,error_msg=get_Status_code(dataset_df) # extract the status_code and error_msg  from dataset_df
                                logging.info("data ingestion : DataDetailClass : GET Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                        else:
                                logging.info("data ingestion : DataDetailClass : GET Method : execution stop : status_code :200")
                                json_data=get_json_format(dataset_df,['dataset_id','index']) 
                                return Response({"status_code":"200","error_msg":"successfull retrival","response":json_data})  #return Data             
                except Exception as e:
                        logging.error("data ingestion : DataDetailClass : GET Method : Exception :" + str(e))
                        logging.error("data ingestion : DataDetailClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 


class DeleteProjectDetailClass(APIView):
        """
        This class is used to delete project detail.
        It will take url string as mlaas/ingest/delete/project_detail/.

        Args   : 
                User_name[(String)]   :[Name of user]
                project_id[(Integer)] :[ID of project]
                
        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """  
        def delete(self, request, format=None):
                try:
                        logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution start")
                        # user_name=request.user.get_username()
                        user_name=request.query_params.get('user_name') # get username
                        project_id=request.query_params.get('project_id')  #get tablename 
                        project_status= IngestionObj.delete_project_details(project_id,user_name)  #get the project_status if project Deletion failed or successfull
                        if project_status != 0:
                                status_code,error_msg=get_Status_code(project_status) # extract the status_code and error_msg from  project_status
                                logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                logging.info("data ingestion : DeleteProjectDetailClass : DELETE Method : execution stop : status_code :200")
                                return Response({"status_code":"200","error_msg":"Successfully Delete","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : DeleteProjectDetailClass : DELETE Method :  Exception : " + str(e))
                        logging.error("data ingestion : DeleteProjectDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 

class DeleteDatasetDetailClass(APIView):
        """
        This class is used to delete Dataset detail.
        It will take url string as mlaas/ingest/delete/dataset_detail/.

        Args   : 
                User_name[(String)]   :[Name of user]
                dataset_id[(Integer)] :[ID of dataset]

        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """
        def delete(self, request, format=None):
                try:
                        logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution start")
                        # user_name=request.user.get_username()
                        user_name=request.query_params.get('user_name') #get user_name
                        dataset_id=request.query_params.get('dataset_id')  #get dataset_name
                        dataset_status=IngestionObj.delete_dataset_detail(dataset_id,user_name) #get the dataset_status if dataset Deletion failed or successfull 
                        if dataset_status != 0:
                                status_code,error_msg=get_Status_code(dataset_status) # extract the status_code and error_msg from dataset_status
                                logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                logging.info("data ingestion : DeleteDatasetDetailClass : DELETE Method : execution stop : status_code :200")
                                return Response({"status_code":"200","error_msg":"Successfully Deleted","response":"true"})

                except Exception as e:
                        logging.error("data ingestion : DeleteDatasetDetailClass : DELETE Method : Exception : " + str(e))
                        logging.error("data ingestion : DeleteDatasetDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 

class DeleteDataDetailClass(APIView):
        """
        This class is used to delete data(CSV) detail.
        It will take url string as mlaas/ingest/delete/data_detail/.

        Args  : 
                user_name[(String)]  :  [Name of the user]
                table_name[(String)] :  [Name of the table]
        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """
        def delete(self, request, format=None):

                try:
                        logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution start")
                        # user_name=request.user.get_username()
                        user_name=request.query_params.get('user_name')
                        table_name=request.query_params.get('table_name')  #get tablename
                        data_detail_status=IngestionObj.delete_data_detail(table_name,user_name) 
                        if data_detail_status != 0 :
                                status_code,error_msg=get_Status_code(data_detail_status) # extract the status_code and error_msg from data_detail_status
                                logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution stop : status_code :"+status_code)
                                return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"}) 
                        else:
                                logging.info("data ingestion : DeleteDataDetailClass : DELETE Method : execution stop : status_code :200")
                                return Response({"status_code":"200","error_msg":"Successfully Deleted","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : DeleteDataDetailClass : DELETE Method : Exception :" + str(e))
                        logging.error("data ingestion : DeleteDataDetailClass : DELETE Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":str(e),"response":"false"}) 


class ToggleLogs(APIView):
        def get(self,request,format=None):
                reader_obj = open(r'Mlaas/settings.py','r')
                settings_string = reader_obj.read()
                logging_line_index = settings_string.find("LOGGING")
                bracket_index = settings_string.find("(",logging_line_index)
                bracket_index+=1
                
                if settings_string[bracket_index] == 'T':
                        settings_string = settings_string[:bracket_index] + "False" + settings_string[bracket_index+4:]
                        logging_status = "False"
                else:
                        settings_string = settings_string[:bracket_index] + "True" + settings_string[bracket_index+5:]
                        logging_status = "True"
                
                reader_obj.close()
                
                writer_obj = open(r'Mlaas/settings.py','w')
                writer_obj.write(settings_string)
                
                writer_obj.close()
                
                return Response({"msg":f"Logging Status changed to {logging_status}"})

class ProjectExistClass(APIView):
        """
        This class is used to Check ProjectName already exist or not.
        It will take url string as mlaas/ingest/project_exist/.

        Args  : 
                user_name[(String)] : [Name of the user]
                project_name[(String)] : [Name of the project]
        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """
        def get(self,request,format=None):
                logging.info("data ingestion : ProjectExistClass : GET Method : execution start")
                user_name = request.query_params.get('user_name') #get user_name
                project_name =request.query_params.get('project_name') #get project_name
                projectexist_status=IngestionObj.does_project_exists(project_name,user_name) # get status
                if projectexist_status != False:
                        status_code,error_msg=get_Status_code(projectexist_status) # extract the status_code and error_msg from projectexist_status
                        logging.info("data ingestion : ProjectExistClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : ProjectExistClass : GET Method : execution stop : status_code :200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":"true"})  
class DatasetExistClass(APIView):
        """
        This class is used to Check Dataset already exist or not.
        It will take url string as mlaas/ingest/dataset_exist/.


        Args  : 
                user_name[(String)] : [Name of the user]
                dataset_name[(String)] : [Name of the dataset]
        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """
        def get(self,request,format=None):
                logging.info("data ingestion : DatasetExistClass : GET Method : execution start")
                user_name = request.query_params.get('user_name') #get user_name
                dataset_name = request.query_params.get('dataset_name') #get dataset_name
                datasetexist_status=IngestionObj.does_dataset_exists(dataset_name,user_name) #get the status if dataset exist or not 
                if datasetexist_status != False:
                        status_code,error_msg=get_Status_code(datasetexist_status) # extract the status_code and error_msg from datasetexist_status
                        logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : DatasetExistClass : GET Method : execution stop : status_code :200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":"true"})  

class DatasetNameClass(APIView):
        """
        This class is used to get All Dataset name which are uploaded.
        It will take url string as mlaas/ingest/datasetname_exist/.


        Args  : 
                user_name[(String)] : [Name of the user]
        Return : 
                status_code(500 or 200),
                error_msg(Error message for deletion failed or successfull),
                Response(false or true)
        """
        def get(self,request,format=None):
                logging.info("data ingestion : DatasetNameClass : GET Method : execution start")
                user_name =request.query_params.get('user_name') #get user_name
                dataset_df=IngestionObj.show_dataset_names(user_name) #retrive all dataset name for that perticular user_name
                if isinstance(dataset_df,str): #check the instance of dataset_df
                        status_code,error_msg=get_Status_code(dataset_df) # extract the status_code and error_msg from dataset_df
                        logging.info("data ingestion : DatasetNameClass : GET Method : execution stop : status_code :"+status_code)
                        return Response({"status_code":status_code,"error_msg":error_msg,"response":"false"})
                else:
                        logging.info("data ingestion : DatasetNameClass : GET Method : execution stop : status_code : 200")
                        return Response({"status_code":"200","error_msg":"you can proceed","response":dataset_df})
        

class MenuClass(APIView):
        def post(self, request, format=None):
                try:
                        logging.info("data ingestion : MenuClass : POST Method : execution start")
                        menu_df=DBObject.read_data('ingest/Menu.csv')
                        status=DBObject.load_csv_into_db(connection_string,'menu_tbl',menu_df,'mlaas')
                        if status != 0:
                                logging.info("data ingestion : MenuClass : POST Method : execution stop : status_code :500")
                                return Response({"status_code":"500","error_msg":"Insertion Failed","response":"false"})
                        else:
                                logging.info("data ingestion : MenuClass : POST Method : execution stop : status_code : 200")
                                return Response({"status_code":"200","error_msg":"Insertion successfull","response":"true"})
                except Exception as e:
                        logging.error("data ingestion : MenuClass : GET Method : Exception :" + str(e))
                        logging.error("data ingestion : MenuClass : GET Method : " +traceback.format_exc())
                        return Response({"status_code":"500","error_msg":"Failed","response":str(e)}) 
        
        def get(self, request, format=None):
                try:
                        logging.info("data ingestion : MenuClass : POST Method : execution start")
                        sql_command1='select id,modulename,menuname as "label",url as "link",parent_id as "parentId",icon from mlaas.menu_tbl where parent_id is null'
                        dataset_df1=DBObject.select_records(connection,sql_command1) #call show_data_details and it will return dataset detail data in dataframe
                        dataset_json1=json.loads(dataset_df1.to_json(orient='records'))  # convert datafreame into json
                        sql_command2='select id,modulename,menuname as "label",url as "link",parent_id as "parentId",icon from mlaas.menu_tbl where parent_id is not null'
                        dataset_df2=DBObject.select_records(connection,sql_command2) #call show_data_details and it will return dataset detail data in dataframe
                        dataset_json2=json.loads(dataset_df2.to_json(orient='records'))  # convert datafreame into json
                        json_data=menu_nested_format(dataset_json1,dataset_json2)   
                        return Response({"status_code":"200","error_msg":"Menu Data","response":json_data})
                except Exception as e:
                        logging.error("data ingestion : MenuClass : POST Method : Exception :" + str(e))
			# logging.error("data ingestion : MenuClass : POST Method : "+ traceback.format_exc())
                        return Response({"status_code":"500","error_msg":"Failed","response":str(e)})

class PaginationClass(APIView):
        """
        this class used to get the fixed length of records with option to search and sorting 
        It will take url string as mlaas/ingest/user/login/.

        Args : 
                start_index[(Integer)] : [value of the starting index]
                length[(Integer)] :[value of length of records to be shown]
                sort_type[(String)] : [value of sort_type ascending or descending]
                column_index[(Integer)] : [index value of the column to perform sorting]
                global_index[(String)] : [value that need be search in table]
                table_name[(String)] : [name of the table]
        Return : 
                [json] : [It will return json formatted data of table ]
        """
        def post(self,request, format=None):
                start_index = request.POST.get('index')
                length = request.POST.get('length')
                sort_type= request.POST.get('sort_type')
                column_index= request.POST.get('column_index')
                global_index = request.POST.get('global_index')
                table_name = request.POST.get('table_name')
                DBObject=db.DBClass()
                data=DBObject.pagination(connection,table_name,global_index,int(start_index),int(length),sort_type,column_index)
                return Response({"Response":data})