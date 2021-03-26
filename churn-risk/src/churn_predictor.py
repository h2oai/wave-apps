import h2o
from typing import Tuple, Any, Union
from h2o.estimators.gbm import H2OGradientBoostingEstimator


class ChurnPredictor:
    """
    Wrapper for H2O-3

    ChurnPredictor builds an abstraction between H2O-3 machine learning library and the Churn Risk app
    giving the developer freedom to integrate any 3rd party machine library with a minimal change to the app code.
    """

    def __init__(self):
        h2o.init()
        # Initialize H2O-3 model and tests data set
        self.train_df = h2o.import_file(path='./data/churnTrain.csv', destination_frame="telco_churn_train.csv")

        train, valid = self.train_df.split_frame([0.8])
        self.model = H2OGradientBoostingEstimator(model_id="telco_churn_model", seed=1234)
        self.model.train(x=self.train_df.columns, y="Churn?", training_frame=train, validation_frame=valid)

        self.h2o_test_df = h2o.import_file(path='./data/churnTest.csv', destination_frame="telco_churn_test.csv")
        self.predicted_df = self.model.predict(self.h2o_test_df).as_data_frame()
        self.contributions_df = self.model.predict_contributions(self.h2o_test_df).drop('BiasTerm').as_data_frame()

    def get_churn_rate(self, row_index: int) -> float:
        return round(float(self.predicted_df["TRUE"][row_index]) * 100, 2)

    def get_shap(self, row_index: int) -> list:
        np_row = self.contributions_df.iloc[row_index].to_numpy()
        shap = [(self.contributions_df.columns[i], np_row[i]) for i in range(len(self.contributions_df.columns))]
        shap.sort(key=lambda e : e[1])
        return shap 
    
    def get_negative_explanation(self, row_index: int) -> Tuple[bool, Any, list]:
        return self._get_explanation(self.contributions_df.idxmin(axis=1)[row_index], row_index)

    def get_positive_explanation(self, row_index: int) -> Tuple[bool, Any, list]:
        return self._get_explanation(self.contributions_df.idxmax(axis=1)[row_index], row_index)

    @staticmethod
    def get_python_type(val: Union[str, float, Any]) -> Union[str, float, int]:
        return val if isinstance(val, (str, float)) else val.item()
        
    @classmethod
    def _get_size(cls, group_size, idx: int) -> Union[str, float, int]:
        return 0 if idx > len(group_size) - 1 else cls.get_python_type(group_size[idx])

    def _get_explanation(self, contrib, row_index: int) -> Tuple[bool, Any, list]:
        contrib_col = self.h2o_test_df[contrib]
        partial_plot = self.model.partial_plot(
            self.h2o_test_df, 
            plot=False,
            cols=[contrib],
            nbins=contrib_col.nlevels()[0] + 1 if contrib_col.isfactor()[0] else 20,
            row_index=row_index
        )[0]
        group_by_size = contrib_col.as_data_frame().groupby(contrib).size().values
        rows = [(partial_plot[0][i], partial_plot[1][i], self._get_size(group_by_size, i)) for i in range(len(partial_plot[0]))]
        return isinstance(partial_plot[0][0], float), contrib, rows
