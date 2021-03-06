'''
/*CHANGE HISTORY

--CREATED BY--------CREATION DATE--------VERSION--------PURPOSE----------------------
 Jay Shukla               25-DEC-2020           1.0           Created Class
 
*/
'''

#* Libraries
from scipy import stats
import logging
import math
import pandas as pd
import numpy as np
import json

#* Exceptions
from common.utils.exception_handler.python_exception.common.common_exception import *
from common.utils.exception_handler.python_exception.preprocessing.preprocess_exceptions import *

#* Relative Imports
from ingest.utils.dataset import dataset_creation as dc


dc = dc.DatasetClass()

class ExploreClass:

    def get_attrbt_datatype(self,csv_data,column_name_list,no_of_rows):
        """
        this function used to get proper attribute type for the column in csv file.

        Args : 
            [(csv_data)] : [Pandas.DataFrame containing the data],
            [(column_name_list)] : [List of the column name],
            [(no_of_rows)] : [No of rows in csv data].

        Return :
            [List] : [List of the predicted type attribute for columns]

        """
        
        attribute_type = [] #empty list to append attribute type
        for column_name in column_name_list: #iterate column name list 
            column_data = csv_data[column_name].tolist() #get the specified column data convert into list
            unique_values = list(set(column_data)) #get the set of unique values convert into list
            if (len(unique_values)/no_of_rows) < 0.2 :
                if "," in str(column_data[1]): #check if the comma value present
                    value = "categorical list"
                else :
                    value = "Categorical"
            else:
                value =  "false" #check condition if condition true then set as categorical else false
            if value =="false": 
                datatype_value = csv_data.dtypes.to_dict()[column_name] #get datatype specified for perticular column name
                if datatype_value in ['float64','float32','int32','int64']: #check if int,float,double present then set it "numerical"
                    value = "Continuous"
                elif datatype_value in ['datetime64[ns]']: #check if datetime value present then set it "timestamp"
                    value = "Timestamp"
                elif datatype_value in ['object']:  #check if object type value present then set it "text"
                        value = "Text"
            attribute_type.append(value) #append type attribute value into list 
        
        logging.info("data preprocessing : ExploreClass : get_attribute_datatype : execution stop")    
        return attribute_type
    
    def get_dataset_statistics(self,data_df):
        """
            This class returns all the statistics for the given dataset.
            
            Args:
                data_df([pandas.DataFrame]): [Dataframe containing raw data.]
                
            Returns:
                stats_df ([pandas.Dataframe]): [Dataframe containing all the statistics.]
        """
        
        #? Logical Code Begins
        try:
            data_df.reset_index(drop=True,inplace = True)
            
            added_col = False
            if (type(data_df) is pd.Series):
                arr = [0]*len(data_df)
                series = pd.Series(arr)
                data_df = pd.DataFrame([data_df, series], columns = [data_df.name, 'auto_generated_column'])
                added_col = True
            
            #? Getting Statistics
            stats_df = data_df.describe(include = 'all')
            
            #? Getting Categorical & Continuous Columns
            num_cols = data_df._get_numeric_data().columns
            numerical_columns = list(num_cols)
            predicted_datatypes = self.get_attrbt_datatype(data_df,data_df.columns,len(data_df))
            for i,col in enumerate(data_df.columns):
                if (col in numerical_columns) and (predicted_datatypes[i].startswith('Ca')):
                    numerical_columns.remove(col)
            stats_df = stats_df.T
            
            #? Changing The Column Names
            stats_df.rename(columns = {'unique':'Unique Values'}, inplace = True)    
            stats_df.rename(columns = {'count':'Non-Null Values'}, inplace = True)  
            stats_df.rename(columns = {'mean':'Mean'}, inplace = True)
            stats_df.rename(columns = {'std':'Std'}, inplace = True)    
            stats_df.rename(columns = {'min':'Min Value'}, inplace = True)    
            stats_df.rename(columns = {'max':'Max Value'}, inplace = True)    
            
            try:
                #? Removing unnecessary columns
                stats_df.drop('top',axis=1, inplace=True)
                stats_df.drop('freq',axis=1, inplace=True)
            except:
                #? If the column wasn't already there then
                pass

            #? Changing Column Datatypes
            stats_df['Mean'] = stats_df['Mean'].astype(float)
            stats_df['Std'] = stats_df['Std'].astype(float)
            stats_df['Min Value'] = stats_df['Min Value'].astype(float)
            stats_df['Max Value'] = stats_df['Max Value'].astype(float)
            stats_df['25%'] = stats_df['25%'].astype(float)
            stats_df['50%'] = stats_df['50%'].astype(float)
            stats_df['75%'] = stats_df['75%'].astype(float)
            
            #? Defining All the Columns that are not in the DataFrame.describe() method but are needed for the exploration page
            stats_df["Null Values"] = len(data_df) - stats_df['Non-Null Values']
            stats_df["Null Values"] = stats_df['Null Values'].astype(int)
            stats_df["Non-Null Values"] = stats_df['Non-Null Values'].astype(int)
            stats_df["DataCount"] = len(data_df)
            stats_df['Most Frequency'] = np.NAN
            stats_df['Most Frequent'] = np.NAN
            stats_df['Least Frequency'] = np.NAN
            stats_df['Least Frequent'] = np.NAN
            stats_df['Column Name'] = 0
            stats_df['Plot Values'] = 0
            stats_df['Plot Values'] = stats_df['Plot Values'].astype('object')
            stats_df['Right Outlier Values'] = 0
            stats_df['Right Outlier Values'] = stats_df['Right Outlier Values'].astype('object')
            stats_df['Left Outlier Values'] = 0
            stats_df['Left Outlier Values'] = stats_df['Left Outlier Values'].astype('object')
            stats_df['Outliers'] = 0
            stats_df['Outliers'] = stats_df['Outliers'].astype('object')
            # logging.info(str(data_df) + " datadf 1")
            data_df = data_df.dropna()
            
            # logging.info(str(stats_df) + " checking")
            #? Getting Column Names, Plotting Values of the histogram & Lest Frequent Values
            i = 0
            axislist = []
            # logging.info(str(data_df) + " datadf")
            for col in data_df.columns:
                # logging.error(str(data_df[col]) + " \n "+str(numerical_columns) +  str(col))
                #? Merging Column Names
                stats_df.iloc[i,-5] = col
                #? Getting Histogram/CountPlot Values
                axislist.append(self.get_values(data_df[col],numerical_columns,col))
        
                #? Getting Least Frequent Values & Count, only for the categorical columns
                if self.get_datatype(numerical_columns,col).startswith("Ca"):
                    try:
                        most_frequent, least_frequent, most_occurrence, least_occurrence = self.get_max_min_occurrence(data_df[col])
                        stats_df.iloc[i,-8] = most_frequent
                        stats_df.iloc[i,-9] = most_occurrence
                        stats_df.iloc[i,-6] = least_frequent
                        stats_df.iloc[i,-7] = least_occurrence
                    except:
                        stats_df.iloc[i,-8] = np.NaN
                        stats_df.iloc[i,-9] = np.NaN
                        stats_df.iloc[i,-6] = np.NaN
                        stats_df.iloc[i,-7] = np.NaN
                i += 1
            stats_df['Plot Values'] = axislist
            stats_df['Datatype'] = predicted_datatypes
            
            IQR = stats_df['75%']-stats_df['25%']
            stats_df['open'] = stats_df['25%']-1.5 * IQR
            stats_df['close'] = stats_df['75%']+1.5 * IQR
            
            stats_df['open'] = stats_df['open'].astype(float)
            stats_df['close'] = stats_df['close'].astype(float)
            
            logging.info(str(stats_df) + " checking 0.1")
            #? Getting Outlier Values
            i = 0
            outliers_list = []
            lower_outliers_list = []
            upper_outliers_list = []
            updated_plot_list = []
            unique_list = []
            logging.error(str(stats_df['Plot Values']) +" checking ")
            for col in data_df.columns:
                #? Getting Lower & Upper Limits for the Histogram
                lower_limit = stats_df.iloc[i]['open']
                upper_limit = stats_df.iloc[i]['close']
                #? Getting Edges of the Bins and Values of Each Bins
                
                bin_edges, hists = stats_df.iloc[i]['Plot Values']
                #? Getting Arrays of the Outliers to be plotted
                lower_outliers, upper_outliers, lower_clip, upper_clip = self.get_outlier_hist(hists, bin_edges, upper_limit, lower_limit)
                #? Getting All the outlier values
                outliers_list.append(self.get_outliers(data_df,col,upper_limit,lower_limit))
                
                #? Pulling plot values
                data  = stats_df.iloc[i]['Plot Values']
                x_axis_values = data[0]
                y_axis_values = data[1]
                if col in numerical_columns:
                    #? Adjusting plot values only for the continuous values, because outlier bins will only be seen in the continuous columns
                    try:
                        #? Removing outlier bins from the plot bins
                        if upper_clip != 0:
                            x_axis_values = x_axis_values[lower_clip:-upper_clip]
                            y_axis_values = y_axis_values[lower_clip:-upper_clip]
                        else:
                            x_axis_values = x_axis_values[lower_clip:]
                            y_axis_values = y_axis_values[lower_clip:]
                    except:
                        #? NaN values of lower clip & upper clip will raise exceptions
                        pass 
                    lower_outliers_list.append(lower_outliers)
                    upper_outliers_list.append(upper_outliers)
                    unique_list.append(np.NaN)
                else:
                    #? Count plots of the categorical columns does not need the outlier bins
                    lower_outliers_list.append([[],[]])
                    upper_outliers_list.append([[],[]])
                    unique_list.append(len(data_df[col].unique()))

                updated_plot_list.append([x_axis_values,y_axis_values])
                i += 1 
            
            #? Storing the Values in the dataframe, so that tey can be sent
            stats_df['Right Outlier Values'] = upper_outliers_list
            stats_df['Left Outlier Values'] = lower_outliers_list
            stats_df['Outliers'] = outliers_list
            stats_df['Plot Values'] = updated_plot_list
            stats_df['Unique Values'] = unique_list
            
            #? Adding a column needed for the frontend
            stats_df['IsinContinuous'] = [True if stats_df.loc[i,'Datatype'] == 'Continuous' else False for i in stats_df.index]
            logging.info(str(stats_df) + " checking 0.2")
            #? Dataset Contains both Categorical & Continuous Data
            try:

                logging.info(str(stats_df) + " checking 0")
                stats_df = stats_df[['Plot Values','Left Outlier Values','Right Outlier Values','Outliers','IsinContinuous','Column Name','Datatype','DataCount','Mean','Std','Min Value','25%','50%','75%','Max Value','Most Frequent','Most Frequency','Least Frequent','Least Frequency','Unique Values','Null Values','Non-Null Values','open','close']]
            
            except KeyError:
                try:
                    #? Dataset Contains only Continuous Data
                    stats_df = stats_df[['Plot Values','Left Outlier Values','Right Outlier Values','Outliers','IsinContinuous','Column Name','Datatype','DataCount','Mean','Std','Min Value','25%','50%','75%','Max Value','Null Values','Non-Null Values','open','close']]
                    logging.info(str(stats_df) + " checking 1")
                except KeyError:
                    #? Dataset Contains only Categorical Data
                    stats_df = stats_df[['Plot Values','Left Outlier Values','Right Outlier Values','Outliers','IsinContinuous','Column Name','Datatype','DataCount','Most Frequent','Most Frequency','Least Frequent','Least Frequency','Unique Values','Null Values','Non-Null Values']]
                    logging.info(str(stats_df) + " checking 2")
        except Exception as exc:
            logging.info(str(exc) + " error")
            return 2
        
        if added_col:
            stats_df.drop(labels = ['auto_generated_column'], axis = 0,inplace = True)

        return stats_df.iloc[1:].round(2)    
    
    def iqr(self,arr):
        '''
            Returns Interquartile range of values in the given array.
            #! Array must be in a sorted form.
            
            Args: 
                List[(Intiger|Float)]: Array containing all the values.
                
            Returns:
                (Intiger|Float): Inter Quartile Range.
        '''
        
        #? Get Interquartile Range
        i_q_r = stats.iqr(arr, interpolation = 'midpoint') 
        return i_q_r

    def get_bin_size_width(self,arr,sort = False):
        '''
            Returns Optimal Number of Bins for the histogram.
            
            Arguments:
                List[(Intiger|Float)]: Array containing all the values.
                sort[(Boolean)] (Default: False): Do you want to sort the array or not?
                
            Returns:
                (Intiger): Number of Bins.
        '''
        
        if sort: arr.sort()
        i_q_r = self.iqr(arr)
        n = len(arr)
        if n==0:
            return 0
        #? Getting optimal number of bins
        number_of_bins = (2*(i_q_r/(n**(1/3))))
        number_of_bins = math.ceil(number_of_bins)
        if number_of_bins < 10: number_of_bins = 10
        
        return number_of_bins
    
    def get_histogram_values(self,arr):
        '''
            Returns the List Containing 2 Lists,  
                1) Bin Edge values (for X-axis).
                2) Histogram values for bins (For Y-axis).
                
            Arguments:
                List[(Intiger|Float)]: Array containing all the values.
                
            Returns:
                List[(Intiger|Float)]: List of 2 Lists containing bin_edges & histogram values.

        '''
        
        try:
            #? Sorting the array
            arr.sort()
            #? Getting the optimal number of bins
            number_of_bins = self.get_bin_size_width(arr)
            #? Limiting the number of bins in a diagram to 20
            if number_of_bins > 20: number_of_bins = 20
            elif number_of_bins < 2: number_of_bins = 2
            #? Getting histogram values & bin_edges
            hist, bin_edges = np.histogram(a=arr, bins=number_of_bins)
            return [bin_edges[:-1].tolist(),hist.tolist()]
        
        except (Exception) as exc:
            return exc
        
    def get_count_plot(self,arr):
        '''
            Returns values for the count plot. This function will be used when the
            column is categorical.
            
            Args:
                List(pandas.Series): Takes Categorical data as pandas.Series object.
                
            Returns:
                List[(String|Intiger)]: Retruns List of 2 lists containing,
                    1) Classes: For X-axis
                    2) Values: For Y-axis
        '''
        unique_values = arr.value_counts()
        classes = list(unique_values.index)
        values = unique_values.tolist()
        
        #? If there are more than 50 bins than the count plot is not suitable
        #? Resizing the countplot
        if len(values) > 50:
            stepsize = int(np.ceil(len(values)/50))
            classes = classes[::stepsize]
            values = values[::stepsize]
        
        return [classes, values]
    
    def get_values(self,arr,numerical,col_name):
        '''
            This function handles plot values for Categorical & Continuous Data.
            
            Args:
                arr[(Intiger|Float|String)]: Takes pandas.Series object as input.
                numerical[List(String)]: Names of numerical columns.
                col_name[String]: Name of the current column.
                
            Returns:
                List[(Intiger|Float|String)]: Returns Values.
        '''
        
        if col_name in numerical:
            check = self.get_histogram_values(arr.tolist()) 
            return check
        else:
            return self.get_count_plot(arr)
        
        
    def get_datatype(self,numerical,col_name):
        '''This function bifurcate Continuous or Categorical Datatype
        Args:
                arr[(Intiger|Float|String)]: Takes pandas.Series object as input.
                numerical[List(String)]: Names of numerical columns.
                col_name[String]: Name of the current column.
                
            Returns:
                datatype[String] : Continuous/Categorical
        '''
        
        if col_name in numerical:
            datatype = "Continuous"
            return datatype
        else:
            datatype = "Categorical"
            return datatype
        

    def get_outlier_hist(self,hist,bin_edges,upper_limit,lower_limit):
        '''
            This Function returns the values for Outlier Bins to be plotted in the
            Histogram.
            
            Args:
                hist[(List of Intigers)]: Y-axis values for each bins,
                bin_edges[(List of Intigers)]: X-axis values for each bins,
                upper_limit[(Intiger)]: Upper limit for the Normal Values, 
                lower_limit[(Intiger)]: Lower limit for the Normal Values.
            
            Returns:
                lower_outliers[(List of Lists)]: Histogram Values for Lower Outliers.
                upper_outliers[(List of Lists)]: Histogram Values for Upper Outliers.
                lower_edges_length[(Intiger)]: How many left side outlier bins (lower outlier bins) are there in the histogram.
                upper_edges_length[(Intiger)]: How many right side outlier bins (upper outlier bins) are there in the histogram.
        '''
        try:
            lower_edges = list(filter(lambda x: x<lower_limit,bin_edges))
            lower_hist = hist[:len(lower_edges)]
            upper_edges = list(filter(lambda x: x>upper_limit,bin_edges))
            if len(upper_edges) == 0:
                upper_hist = []
            else:
                upper_hist = hist[-len(upper_edges):]

            upper_outliers = [upper_edges,upper_hist]
            lower_outliers = [lower_edges,lower_hist]

            return lower_outliers, upper_outliers, len(lower_edges), len(upper_edges)
        except:
            return [[],[]],[[],[]], np.NaN, np.NaN
        
    def get_outliers(self,df,col,upper_limit,lower_limit):
        '''
            This Function Returns the Values of all the Outliers.
            This function is used to get outlier values for the Box-Plot.
            
            Args:
                df[(pandas.DataFrame)]: DataFrame Containing the Dataset which is to be explored.
                col[(String)]: Columns name
                upper_limit[(Intiger)]: Upper Limit of the Normal Values
                lower_limit[(Intiger)]: Lower Limit of the Normal Values
                
            ReturnsL
                List[(List of Intigers)]: List containing the outliers to be plotted in the box plot.
        '''
        try:
            partial_list_1 = df[df[col] < lower_limit][col]
            partial_list_2 = df[df[col] > upper_limit][col]
            return list(set(partial_list_1.tolist() + partial_list_2.tolist()))
        except:
            return []
        
    def get_max_min_occurrence(self, series):
        '''
            Takes pandas.Series as an input and returns occurrence related information.
            
            Args:
                series(pandas.Series): Column data.
                
            Returns:
                most_frequent(Intiger|String): Most occurring element in the column.
                least_frequent(Intiger|String): Least occurring element in the column.
                most_occurrence(Intiger): Frequency count of the Most occurring element.
                least_occurrence(Intiger): Frequency count of the least occurring element.
        '''
        
        try:
            value_count = series.value_counts()
            count_list = list(value_count)
            
            #? No value in the column
            if len(count_list) == 0:
                return np.NaN,np.NaN,np.NaN,np.NaN
            
            #? Only one value repeating in the column
            if len(count_list) == 1:
                return value_count.index[0],value_count.index[0],count_list[0],count_list[0]
            
            #? Are there multiple lease or most frequent values with the same frequency
            multiple_least_occ = False
            multiple_most_occ = False
            if count_list[-1] == count_list[-2]:
                multiple_least_occ = True
            if count_list[0] == count_list[1]:
                multiple_most_occ = True
                
            #? Both most frequent & least frequent values have multiple values with the same frequency
            if multiple_least_occ and multiple_most_occ:
                return '*','*',count_list[0],count_list[-1]
            
            #? Only least frequent values have multiple values with the same frequency
            elif multiple_least_occ:
                return value_count.index[0],'*',count_list[0],count_list[-1]
            
            #? Only most frequent values have multiple values with the same frequency
            elif multiple_most_occ:
                return '*',value_count.index[-1],count_list[0],count_list[-1]
            
            #? Most Frequent & Least frequent values don't have any other values with same frequency of occurrence
            else:
                return value_count.index[0],value_count.index[-1],count_list[0],count_list[-1]
        
        except:
            return np.NaN,np.NaN,np.NaN,np.NaN