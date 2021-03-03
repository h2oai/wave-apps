import pandas as pd
from datetime import datetime


def update_df(df: pd.DataFrame, image_path: str):
    temp = pd.DataFrame({
        'Image': [image_path],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    return df.append(temp, ignore_index=True)
