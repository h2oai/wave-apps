import pandas as pd
import src.app as app


df = pd.read_csv("test/unit/data/sanitize.csv")
id_column = "Phone_No"
international_plan_default = 'no'
no_cs_calls_default = 0.0
phone_missing_mandatory_attribute = 3548815
phone_missing_numeric_attribute =  3653009
phone_missing_string_attribute = 3817211

def test_sanitize_dataframe_with_empty_numeric_attribute():
    app.sanitize_dataframe(df)
    no_cs_calls = df.loc[df[id_column] == phone_missing_numeric_attribute]['No_CS_Calls'].values[0]
    assert no_cs_calls == no_cs_calls_default


def test_sanitize_dataframe_with_empty_string_attribute():
    app.sanitize_dataframe(df)
    international_plan = df.loc[df[id_column] == phone_missing_string_attribute]['International_Plan'].values[0]
    assert international_plan == international_plan_default


def test_sanitize_dataframe_with_empty_mandatory_attribute():
    app.sanitize_dataframe(df)
    empty_mandatory_column = df.loc[df[id_column] == phone_missing_mandatory_attribute]
    assert empty_mandatory_column.empty
