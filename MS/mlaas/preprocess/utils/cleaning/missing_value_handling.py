import pandas as pd
import numpy as np
import logging
from common.utils.logger_handler import custom_logger as cl

user_name = 'admin'
log_enable = True
LogObject = cl.LogClass(user_name,log_enable)
LogObject.log_setting()
logger = logging.getLogger('missing_value_handling')


class MissingValueClass:

    def discard_missing_values(self, dataframe, column_id = None):
        '''
            Returns a dataframe where all the rows where given columns have null values are removed.
            
            Args:
            -----
            dataframe (`pandas.Dataframe`): Whole Dataframe.
            column_id (`List`) (default = `None`): List of Columns. If `None` then considers whole dataframe.

            Returns:
            -------
            dataframe (`pandas.Dataframe`): Dataframe with all the missing data removed.
        '''
        
        if column_id:
            
            for i in column_id:
            
                dataframe.dropna(subset=[dataframe.columns[i]], inplace = True)
                
            return dataframe
        
        else:
            return dataframe.dropna()
    
    def mean_imputation(self,series):
        """
        Function will replace column NaN value with its column mean value
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
        Return:
                series[(pandas.Series)] : [return the updated series]  

        """
        logging.info("Preprocess : MissingValueClass : mean_imputation : execution start")
        
        #Replace the NaN value with mean of the column 
        series.fillna(round(series.mean(),4), inplace = True)

        logging.info("Preprocess : MissingValueClass : mean_imputation : execution stop")
        return series
    
    def median_imputation(self,series):
        """
        Function will replace column NaN value with its column median value
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
        Return:
                series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : median_imputation : execution start")

        #Replace the NaN value with median of the column 
        series.fillna(round(series.median(),4),inplace = True)

        logging.info("Preprocess : MissingValueClass : median_imputation : execution stop")
        return series
    
    def mode_imputation(self,series):
        """
        function will replace column NaN value with its column mode value
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
        Return:
                series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : mode_imputation : execution start")

        #Replace the NaN value with Mode of the column
        series = series.fillna(round(series.mode()),inplace = True)

        logging.info("Preprocess : MissingValueClass : mode_imputation : execution stop")
        return series
    
    def end_of_distribution(self,series):
        """
        Returns a series with missing values replaced by a maximum value that is not an outlier.
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
        Return:
                series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : end_of_distribution : execution start")

        #get the extreme distribution value based on the formula
        extreme = series.mean()+3*series.std()

        #replace the NaN value extreme distribution value
        series.fillna(round(extreme,4),inplace = True)

        logging.info("Preprocess : MissingValueClass : end_of_distribution : execution stop")
        return series
    
    def random_sample_imputation(self,series):
        """
        Function will replace column NaN value with random values
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
        Return:
                series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : random_sample_imputation : execution start")
        
        ## it will have the random sample to fill NaN value
        random_sample = series.dropna().sample(series.isnull().sum(),random_state=1)

        ## pandas need to have same index in order to merge the dataset
        random_sample.index = series[series.isnull()].index

        #insert the random number into its specific index location
        series.loc[series.isnull()] = random_sample
        
        logging.info("Preprocess : MissingValueClass : random_sample_imputation : execution stop")

        return series
    

    def add_missing_category(self,series, val = "Missing"):
        """
        Function will replace column NaN value with "Missing"  category name
        
        Args:
                series[(pandas.Series)] : [the Series containing the column data]
                val[(String)] (default = `Missing`): [Value of the category.]
        Return:
                series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : add_missing_category : execution start")
        
        #add the "Missing" category where it find the NaN value
        series = np.where(series.isnull(),val,series)

        logging.info("Preprocess : MissingValueClass : add_missing_category : execution stop")
        return series
    
    def frequent_category_imputation(self,series):
        """
        Function will replace column NaN value with most frequent used category name
        
        Args:
            series[(pandas.Series)] : [the Series containing the column data]
        Return:
            series[(pandas.Series)] : [return the updated series]
        """
        logging.info("Preprocess : MissingValueClass : frequent_category_imputation : execution start")

        #get the most occuring category
        frequent_category = series.value_counts().index[0]

        #Replace the NaN value with most occuring category
        series.fillna(frequent_category,inplace = True)
        
        logging.info("Preprocess : MissingValueClass : frequent_category_imputation : execution stop")
        return series