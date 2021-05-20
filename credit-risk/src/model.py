import h2o
import pandas as pd

from h2o.estimators.gbm import H2OGradientBoostingEstimator


class Model:
    """
    Model builds an abstraction between H2O-3 machine learning library and 
    the app giving the developer freedom to integrate any 3rd party machine 
    library with a minimal change to the app code.
    """

    def __init__(self, train_csv: str, id_column: str, target_column: str) -> None:
        h2o.init()

        self._model = None
        self._id_column = id_column
        self._target_column = target_column
        self._train_df = h2o.import_file(path=train_csv)

    @property
    def model(self):
        if not self._model:
            y = self._target_column
            x = self._train_df.columns
            x.remove(y)
            x.remove(self._id_column)
            train, valid = self._train_df.split_frame([0.8])
            self._model = H2OGradientBoostingEstimator(seed=1)
            self._model.train(x=x, y=y, training_frame=train, validation_frame=valid)
        return self._model

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.model.predict(h2o.H2OFrame(data)).as_data_frame().iloc[:,-1]

    def contrib(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.model.predict_contributions(h2o.H2OFrame(data)).as_data_frame()
