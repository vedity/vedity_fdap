
import pandas as pd 
from database import *
from common.utils.database import db

# from . import db

class ModelSqlClass:
    
    def __init__(self,database,user,password,host,port):
        # DataBase Credintials 

        self.DBObject = db.DBClass()
        self.connection,self.connection_string = self.DBObject.database_connection(database,user,password,host,port)
        
    def create_model_experiment(self):
        
        table_name = "mlaas.model_experiment_tbl"
        
        schema = "exp_unq_id bigserial,"\
                 "experiment_id  integer,"\
                 "run_uuid text,"\
                 "project_id bigint,"\
                 "dataset_id bigint,"\
                 "user_id integer,"\
                 "model_id  integer,"\
                 "model_mode  text,"\
                 "exp_created_on TIMESTAMPTZ NOT NULL DEFAULT NOW()"
                       
                       
        create_status = self.DBObject.create_table(self.connection,table_name,schema)
         
        return create_status              
                       
    def create_model_master(self):
        
        table_name = "mlaas.model_master_tbl"
        
        schema = "model_id integer,"\
                      "model_name text,"\
                      "model_desc text,"\
                      "model_parameter text,"\
                      "model_type text,"\
                      "algorithm_type text"
                      
        create_status = self.DBObject.create_table(self.connection,table_name,schema)
         
        return create_status    
                  

    def clean_up_reference(self):
        
        project_id = 2
        dataset_id = 2
        user_id = 2
        
        input_features = "['index','bedrooms','bathrooms','sqft_living','sqft_lot','floors','waterfront','view','condition','grade','sqft_above','sqft_basement','yr_built','yr_renovated','zipcode','lat','long','sqft_living15','sqft_lot15']"
        target_features = "['index','price']"
        
        scaled_data_table = "kc_house_data"  
        
        row=project_id,dataset_id,user_id,input_features,target_features,scaled_data_table 
        row_tuples = [tuple(row)] 
        
        return row_tuples
    
    
    def create_reference_table(self):
        
        table_name = "mlaas.cleaned_ref_tbl"
        
        schema = "unq_id bigserial,"\
                 "project_id integer,"\
                 "dataset_id integer,"\
                 "user_id integer,"\
                 "input_features text,"\
                 "target_features text,"\
                 "scaled_data_table text"
                      
                        
        create_status = self.DBObject.create_table(self.connection,table_name,schema)
         
        return create_status   
                        
    def load_scaled_data(self):
        
        file_data_df = pd.read_csv('kc_house_data.csv')
        user_name = "mlaas"
        table_name = "kc_house_data"
        load_status = self.DBObject.load_df_into_db(self.connection_string,table_name,file_data_df,user_name)
        return load_status
    
    def add_ref_record(self):
        table_name = 'mlaas.cleaned_ref_tbl'
        row_tuples = self.clean_up_reference()
        cols = 'project_id,dataset_id,user_id,input_features,target_features,scaled_data_table'
        ref_status = self.DBObject.insert_records(self.connection,table_name,row_tuples,cols)
        
        return ref_status
    
    def add_model_records(self):
        
        table_name = 'mlaas.model_master_tbl'
        cols = 'model_id,model_name,model_desc,model_parameter,model_type,algorithm_type'
        
        # First Model
        model_id = 1
        model_name = "Linear_Regression_Sklearn"
        model_desc = "This is simple linear model"
        model_parameter = None
        model_type = "Regression"
        algorithm_type = "Single_Target"
        
        row=model_id,model_name,model_desc,model_parameter,model_type,algorithm_type 
        row_tuples = [tuple(row)] 

        ref_status = self.DBObject.insert_records(self.connection,table_name,row_tuples,cols)
        
        # Second Model
        
        model_id = 2
        model_name = "Linear_Regression_Keras"
        model_desc = "This is simple linear model with keras"
        model_parameter = "['lr','batch_size','epoch','optimizer','loss','activation']"
        model_type = "Regression"
        algorithm_type = "Single_Target"
        
        row=model_id,model_name,model_desc,model_parameter,model_type,algorithm_type 
        row_tuples = [tuple(row)] 
        
        ref_status = self.DBObject.insert_records(self.connection,table_name,row_tuples,cols)
        
        
        
        # Third Model
         # Second Model
        
        model_id = 3
        model_name = "XGBoost_Regressor"
        model_desc = "This is simple linear ensemble model"
        model_parameter = None
        model_type = "Regression"
        algorithm_type = "Single_Target"
        
        row=model_id,model_name,model_desc,model_parameter,model_type,algorithm_type 
        row_tuples = [tuple(row)] 
        
        ref_status = self.DBObject.insert_records(self.connection,table_name,row_tuples,cols)
        
        return ref_status
        
  
 
# DataBase Credintials  
     
ModelSqlObject = ModelSqlClass(database,user,password,host,port)

model_exp_status = ModelSqlObject.create_model_experiment()
print("model_exp_status == ",model_exp_status)
model_mst_status = ModelSqlObject.create_model_master()
print("model_mst_status == ",model_mst_status)
cln_ref_status = ModelSqlObject.create_reference_table()
print("cln_ref_status == ",cln_ref_status)
load_status = ModelSqlObject.load_scaled_data()
print("load_status == ",load_status)
ref_status = ModelSqlObject.add_ref_record()
print("ref_status == ",ref_status)
ref_status = ModelSqlObject.add_model_records()
print("ref_status == ",ref_status)





        
        
        
   

        
        
        
    
    
