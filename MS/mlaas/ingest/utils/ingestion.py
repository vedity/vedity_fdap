'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Vipul Prajapati          07-DEC-2020           1.0           Initial Version 
 Vipul Prajapati          08-DEC-2020           1.1           Modification for Business Rule ****************************************************************************************/

*/
'''
import pandas as pd 
from common.utils.database import db
from .project.project_creation import *
from .dataset import dataset_creation as dt
from .project import project_creation as pj
from common.utils.exception_handler.python_exception import *

class IngestClass(pj.ProjectClass,dt.DatasetClass):

    def __init__(self,database,user,password,host,port):
        """This constructor is used to initialize database credentials.
           It will initialize when object of this class is created with below parameter.
           
        Args:
            database ([string]): [name of the database.],
            user ([string]): [user of the database.],
            password ([string]): [password of the database.],
            host ([string]): [host ip or name where database is running.],
            port ([string]): [port number in which database is running.]
        """
        self.database = database # Database Name
        self.user = user # User Name
        self.password = password # Password
        self.host = host # Host Name
        self.port = port # Port Number

    def get_db_connection(self):
        """This function is used to initialize database connection.
        
        Returns:
            [object,string]: [it will return database object as well as connection string.]
        """
        DBObject = db.DBClass() # Get database object from database class
        connection,connection_string = DBObject.database_connection(self.database,self.user,self.password,self.host,self.port) # Initialize connection with database and get connection string , connection object.
        return DBObject,connection,connection_string
 
    def create_project(self,project_name,project_desc,dataset_name = None,dataset_visibility = None,file_name = None,dataset_id = None,user_name = None):
        """This function is used to create project.
           E.g. sales forecast , travel time predictions etc.
           
        Args:
            project_name ([string]): [name of the project],
            project_desc ([string]): [descriptions of the project],
            dataset_name ([string], optional): [name of the dataset]. Defaults to None.
            dataset_visibility ([string], optional): [visibility of the dataset]. Defaults to None.
            file_name ([string], optional): [name of the csv file]. Defaults to None.
            dataset_id ([integer], optional): [dataset id of the selected dataset name]. Defaults to None.
            user_name ([string], optional): [name of the user]. Defaults to None.

        Returns:
            [integer]: [status of the project creation. if successfully then 0 else 1.]
        """
        try:
            DBObject,connection,connection_string = self.get_db_connection()
            if connection == None :
                raise DatabaseConnectionFailed(500)
            
            project_status,project_id = super(IngestClass,self).make_project(DBObject,connection,project_name,project_desc,dataset_name,dataset_visibility,file_name ,dataset_id,user_name)

            if project_status == 2:
                raise ProjectAlreadyExist(500)
                
            elif project_status == 1:
                raise ProjectCreationFailed(500) # If Failed.
                
            elif project_status == 0 and dataset_id == None:
                load_data_status = super(IngestClass,self).load_dataset(DBObject,connection,connection_string,file_name,dataset_visibility,user_name)
                if load_data_status == 1:
                    raise LoadCSVDataFailed(500)
                
                status = super(IngestClass,self).update_dataset_status(DBObject,connection,project_id,load_data_status)
                     
            elif project_status == 0:
                status = super(IngestClass,self).update_dataset_status(DBObject,connection,project_id)
                
                
        except (DatabaseConnectionFailed,ProjectAlreadyExist,LoadCSVDataFailed,ProjectCreationFailed) as exc:
            return exc.msg
        
        return project_status

        
    def create_dataset(self,dataset_name,file_name,dataset_visibility,user_name):
        """This function is used to create dataset.
           E.g. sales , traveltime etc.
           
        Args:
            dataset_name ([string]): [name of the dataset.],
            file_name ([string]): [name of the name.],
            dataset_visibility ([string]): [visibility of the dataset.],
            user_name ([string]): [name of the user.]

        Returns:
            [status]: [status of the dataset creation. if successfully then 0 else 1.]
        """
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None:
                raise DatabaseConnectionFailed(500)
            dataset_status,_ = super(IngestClass,self).make_dataset(DBObject,connection,dataset_name,file_name,dataset_visibility,user_name) # Get Status about dataset creation,if successfully then 0 else 1.
            
            if dataset_status == 2:
                raise DatasetAlreadyExist(500)
            
            elif dataset_status == 1 :
                raise DatasetCreationFailed(500)
            # Condition will check dataset successfully created or not. if successfully then 0 else 1.
            elif dataset_status == 0 :
                load_data_status = super(IngestClass,self).load_dataset(DBObject,connection,connection_string,file_name,dataset_visibility,user_name)
                if load_data_status == 1:
                    raise LoadCSVDataFailed(500)

        except (DatabaseConnectionFailed,DatasetAlreadyExist,DatasetCreationFailed,LoadCSVDataFailed) as exc:
            return exc.msg

        return dataset_status
        
    def show_dataset_details(self,user_name):
        """This function is used to show dataset details.

        Args:
            user_name ([string]): [name of the user.]

        Returns:
            [dataframe]: [it will return dataframe of the dataset details.]
        """
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None :
                raise DatabaseConnectionFailed(500)
            
            dataset_df = super(IngestClass,self).show_dataset_details(DBObject,connection,user_name) # Get dataframe of dataset created.
            dataset_df = dataset_df.to_json(orient='records')
            
            if len(dataset_df) == 0 :
                raise DatasetDataNotFound (500)
                 
        except (DatabaseConnectionFailed,DatasetDataNotFound) as exc:
            return exc.msg
         
        
        return dataset_df

    def show_data_details(self,table_name,user_name,dataset_visibility):
        """This function is used to show data details.
           It will show all the columns and rows from uploaded csv files.

        Args:
            table_name ([string]): [name of the  table.]

        Returns:
            [dataframe]: [it will return dataframe of the loaded csv's data.]
        """
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            
            if dataset_visibility.lower() == 'public':
                user_name = 'public'
            
            if connection == None :
                raise DatabaseConnectionFailed(500)
            
            data_details_df = super(IngestClass,self).show_data_details(DBObject,connection,table_name,user_name) # Get dataframe of loaded csv.
            if type(data_details_df) == type(None) :
                raise DataNotFound(23)
            data_details_df=data_details_df.to_json(orient='records')
            if len(data_details_df) == 0 :
                raise DataNotFound(500)
            
            
        except (DatabaseConnectionFailed,DataNotFound) as exc:
            return exc.msg
        
        return data_details_df

    def show_project_details(self,user_name):
        """This function is used to show project details.
        
        Args:
            user_name ([string]): [name of the user]

        Returns:
            [dataframe]: [dataframe of project details data]
        """
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None:
                raise DatabaseConnectionFailed(500)
            
            project_df = super(IngestClass,self).show_project_details(DBObject,connection,user_name) # Get dataframe of project created.
            project_df = project_df.to_json(orient='records')
            if project_df == None or len(project_df) == 0:
                raise ProjectDataNotFound(500)
            
        except (DatabaseConnectionFailed,ProjectDataNotFound) as exc:
            return exc.msg
        
        return project_df
    
    def delete_project_details(self, project_id, user_name):
        '''
        This function is used to delete an entry in the project_tbl
        
        Args:
            project_id ([integer]): [id of the entry which you want to delete.],
            user_name ([string]): [Name of the user.]
            
        Returns:
            status ([boolean]): [status of the project deletion. if successfully then 0 else 1.]
        '''
        
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None:
                raise DatabaseConnectionFailed(500)
            
            deletion_status = super(IngestClass, self).delete_project_details(DBObject,connection,project_id,user_name)
            if deletion_status == 1:
                raise ProjectDeletionFailed(500)
            elif deletion_status == 2:
                raise UserAuthenticationFailed(500)
            
            return deletion_status
        
        except (DatabaseConnectionFailed,ProjectDeletionFailed,UserAuthenticationFailed) as exc:
            return exc.msg
        
    def delete_dataset_details(self, dataset_id, user_name):
        '''
        This function is used to delete an entry in the project_tbl
        
        Args:
            dataset_id ([integer]): [id of the dataset entry which you want to delete.],
            user_name ([string]): [Name of the user.]
            
        Returns:
            status ([boolean]): [status of the project deletion. if successfully then 0 else 1.]
        '''
        
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None:
                raise DatabaseConnectionFailed(500)
            
            deletion_status = super(IngestClass, self).delete_dataset_details(DBObject,connection,dataset_id,user_name)
            if deletion_status == 1:
                raise DatasetDeletionFailed(500)
            elif deletion_status == 2:
                raise DataDeletionFailed(500)
            elif deletion_status == 3:
                raise DatasetInUse(500)
            elif deletion_status == 4:
                raise UserAuthenticationFailed(500)
            
            return deletion_status
        
        except (DatabaseConnectionFailed,DatasetDeletionFailed,DataDeletionFailed,UserAuthenticationFailed,DatasetInUse) as exc:
            return exc.msg
        
    def delete_data_details(self,table_name,user_name):
        """
        This function is used to delete the whole table which was created from 
        user input file.
        
        Args:
            table_name ([string]): [Name of the table that you want to delete.],
            user_name ([string]): [Name of the user.]

        Returns:
            [integer]: [it will return status of the dataset deletion. if successfully then 0 else 1.]
        """
        
        try:
            DBObject,connection,connection_string = self.get_db_connection() # Get database object,connection object and connecting string.
            if connection == None:
                raise DatabaseConnectionFailed(500)
            
            deletion_status = super(IngestClass, self).delete_data_details(DBObject,connection,table_name,user_name)
            if deletion_status == 1:
                raise DataDeletionFailed(500)
            
            return deletion_status
        
        except (DatabaseConnectionFailed,DataDeletionFailed) as exc:
            return exc.msg
        

    
