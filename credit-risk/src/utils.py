def add_column_to_df(to_df, from_df, to_column, from_column):
    to_df[to_column] = from_df[from_column].values


def drop_column_from_df(df, column):
    df.drop([column], axis='columns', inplace=True)


def round_df_column(df, column, decimals=0):
    return df.round({column: decimals})
