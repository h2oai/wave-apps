import h2o
import pandas as pd

from h2o_wave_ml import build_model, ModelType


class Model:
    """
    Model builds an abstraction between WaveML and the app
    giving the developer freedom to integrate any 3rd party machine 
    library with a minimal change to the app code.
    """

    def __init__(self, train_csv: str, id_column: str, target_column: str) -> None:
        self._train_csv = train_csv
        self._id_column = id_column
        self._target_column = target_column
        self._model = None

    @property
    def model(self):
        if not self._model:
            wave_model = build_model(
                train_file_path=self._train_csv,
                target_column=self._target_column,
                model_type=ModelType.H2O3,
                drop_columns=[self._id_column],
                _h2o3_max_runtime_secs=30,
                _h2o3_nfolds=0,
                _h2o3_include_algos=['DRF', 'XGBoost', 'GBM']
            )

            self._model = wave_model.model
        return self._model

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.model.predict(h2o.H2OFrame(data)).as_data_frame().iloc[:,-1]

    def contrib(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.model.predict_contributions(h2o.H2OFrame(data)).as_data_frame()
