def filter_data_frame(df, filters_map):
    for key, value in filters_map.items():
        for attr, attr_value in value.items():
            df = df[df[attr] == attr_value]

    return df
