class Configuration:
    """
    Configuration file for Telco Customer Churn
    """
    def __init__(self):
        self.color = '#00A8E0'
        self.image_path = 'static/churn.png'

        self.training_path = 'data/churnTrain.csv'
        self.testing_path = 'data/churnTest.csv'

        self.y_col = 'Churn'
        self.x_cols = ['Account_Length', 'No_Vmail_Messages', 'Total_Day_minutes', 'Total_Day_Calls',
                       'Total_Day_charge', 'Total_Eve_Minutes', 'Total_Eve_Calls', 'Total_Eve_Charge',
                       'Total_Night_Minutes', 'Total_Night_Calls', 'Total_Night_Charge', 'Total_Intl_Minutes',
                       'Total_Intl_Calls', 'Total_Intl_Charge', 'No_CS_Calls', 'Area_Code', 'International_Plan',
                       'Voice_Mail_Plan', 'State', 'Phone_No']

        self.id_column = "Phone_No"

        self.title = 'Telecom Churn Analytics'
        self.subtitle = 'EDA & Churn Modeling with AutoML & Wave'
        self.icon = 'AddPhone'

        self.model_loaded = False
        self.working_data = self.training_path

    def load_model(self, predictions_file_path):
        self.model_loaded = True
        self.working_data = predictions_file_path

    def get_column_type(self):
        if self.model_loaded:
            return "Churn Prediction"
        else:
            return "Churn"

    def get_analysis_type(self):
        if self.model_loaded:
            return "Model Predictions"
        else:
            return "Historical Data"
