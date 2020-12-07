def filter_data_frame(df, filters_map):
    for key, value in filters_map.items():
        print(key)
        df = df[df[key] == value]

    return df
