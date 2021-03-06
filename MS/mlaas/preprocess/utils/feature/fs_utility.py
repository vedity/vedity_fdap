from pandas import read_csv
import logging
from sklearn.preprocessing import LabelEncoder
from common.utils.database.db import DBClass
from common.utils.database import db
from database import *
import pandas as pd
DBObject = db.DBClass()
connection,connection_string=DBObject.database_connection(database,user,password,host,port) 

class FSUtilityClass():
    def load_dataset(self,df,target_col,Ydata=pd.DataFrame()):

        # load the dataset as a pandas DataFrame
        data = df
        if Ydata.empty:
            y = data[target_col]
        else:
            #target column 'Y' 
            y = Ydata[target_col]
        
        col_exists = target_col in data
        if col_exists:
            X = data.drop(target_col,axis=1)
        else:
            X = data
        X=X.apply(LabelEncoder().fit_transform)
        return X, y

    def get_schema_dtype(self,DBObject,connection,schema_id):

        sql_command = f"select column_name, case when changed_column_name='' then column_name else changed_column_name end column_list from mlaas.schema_tbl st where data_type ='categorical' and schema_id ="+str(schema_id)+"order by index ASC"
        df = DBObject.select_records(connection,sql_command)
        col,change_col = list(df['column_name']),list(df['column_list'])
        col =[x.strip("'") for x in col]
        change_col =[x.strip("'") for x in change_col]
        return col,change_col

    def get_numeric_schema_dtype(self,DBObject,connection,schema_id):

        sql_command = f"select column_name, case when changed_column_name='' then column_name else changed_column_name end column_list from mlaas.schema_tbl st where data_type ='numerical' and schema_id ="+str(schema_id)+"order by index ASC"
        df = DBObject.select_records(connection,sql_command)
        df.drop(df.index[0],inplace= True)
        col,change_col = list(df['column_name']),list(df['column_list'])
        col =[x.strip("'") for x in col]
        change_col =[x.strip("'") for x in change_col]
        return col,change_col


    def fetch_column(self,DBObject,connection,schema_id):
        
        sql_command = f"select column_name, case when changed_column_name='' then column_name else changed_column_name end column_list from mlaas.schema_tbl where schema_id ="+str(schema_id)+" order by index ASC"
        df = DBObject.select_records(connection,sql_command)
        df.drop(df.index[0],inplace= True)
        col,change_col = list(df['column_name']),list(df['column_list'])
        col =[x.strip("'") for x in col]
        change_col =[x.strip("'") for x in change_col]
        return col,change_col


    def selectkbest_extra_column(self,DBObject,connection,schema_id,col_lst,algo_column):

        col,change_col = self.fetch_column(DBObject,connection,schema_id)
        extra = {}
        for i in change_col:
            if i not in col_lst and i not in algo_column:
                extra[i]="True"
            elif i not in col_lst and i in algo_column:
                extra[i]="False"
            else:
                extra[i]="True"
        return extra



