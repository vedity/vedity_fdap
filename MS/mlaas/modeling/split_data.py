from sklearn.model_selection import train_test_split



class SplitData:
    '''
        A Class which maintains the model_mode, split_method, cv, and the ratios for train, test, and validation.

    '''
    def __init__(self, basic_split_parameters, model_id, DBObject, connection):
        # self.split_dataset = split_dataset

        self.split_method = None 
        self.random_state = None
        self.test_size = None
        self.train_size = None
        self.cv = None
        self.valid_size = None

        self.model_mode = basic_split_parameters['model_mode']
        if self.model_mode == 'manual':
            self.split_method, self.random_state, self.test_size, self.train_size, self.cv, self.valid_size = self.get_split_dataset(basic_split_parameters)

        if self.model_mode == 'auto':
            self.split_method, self.random_state, self.test_size, self.train_size, self.cv, self.valid_size = self.get_auto_split_dataset(model_id, DBObject, connection)

        # else:
        #     self.split_method = 'cross_validation'
        #     self.train_size = 0.8
        #     self.test_size = 0.2
        #     self.cv = 5
        #     self.random_state = 0


    def get_split_dataset(self, dataset_split_parameters):
        """Returns the splitting dataset parameters.

        Args:
            dataset_split_parameters (dictionary): [Contains the model_mode, and if required, other necessary parameters.]

        Returns:
            [tuple]: [dataset splitting method, and parameters required to split it.]
        """

        split_method = dataset_split_parameters['split_method']
        random_state = dataset_split_parameters['random_state']
        test_size = dataset_split_parameters['test_size']
        train_size = 1 - test_size
        
        if split_method == 'cross_validation':    
            cv = dataset_split_parameters['cv']
            valid_size = None
        else:
            valid_size = dataset_split_parameters['valid_size']
            cv = None
        # print(split_method, random_state, test_size, train_size, cv, valid_size)
        return split_method, random_state, test_size, train_size, cv, valid_size


    def get_auto_split_dataset(self, model_id, DBObject, connection):
        """This function runs only when the model_mode is 'auto'.

        Args:
            model_name (string): [Name of the ML/DL model]
            DBObject (db): [Database connection object]
            connection (connection): [DB connection]

        Returns:
            [tuple]: [dataset splitting method, and parameters required to split it.]
        """
        # print(model_name)
        # sql_command = "select model_id from mlaas.split_data_params_tbl where model_name='Linear_Regression_With_Sklearn'"
        # model_id = DBObject.select_records(connection, sql_command).iloc[0, 0]
        # print(model_id)
        sql_command = 'select split_method,cv,valid_size,test_size,random_state from mlaas.split_dataset_params_tbl where model_id='+str(model_id)
        dataset_split_parameters = DBObject.select_records(connection, sql_command).iloc[0, :]
        # print(dataset_split_parameters)
        return self.get_split_dataset(dataset_split_parameters)        


    def get_split_data(self, X, y):
        """Returns train-test or train-valid-test split on the basis of split_method.

        Args:
            X (array/DataFrame): Input values.
            y (array/DataFrame): Target values.

        Returns:
            X_train, X_test, Y_train, Y_test or also returns X_valid, Y_valid: Splitted data for train and test.
        """
        if self.split_method == 'cross_validation':
            X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=self.test_size,
                                                                random_state=self.random_state)

            return X_train, None, X_test, Y_train, None, Y_test
        else:
            X_train_valid, X_test, Y_train_valid, Y_test = train_test_split(X, y, test_size=self.test_size,
                                                                        random_state=self.random_state)

            X_train, X_valid, Y_train, Y_valid = train_test_split(X_train_valid, Y_train_valid, test_size=self.valid_size,
                                                            random_state=self.random_state)

            return X_train, X_valid, X_test, Y_train, Y_valid, Y_test 

