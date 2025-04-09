import pandas as pd

csv_file_path = "data/protest_events_gdelt_bq.csv"
parquet_file_path = "data/protest_events_gdelt_bq.parquet"

dtypes = {
    'Year': 'int16',
    'SQLDATE': 'int32',
    'ActionGeo_Lat': 'float32',
    'ActionGeo_Long': 'float32',
    'ActionGeo_FullName': 'category',
    'ProtestCategory': 'category',
    'NumMentions': 'int16',
    'NumArticles': 'int16',
    'HeadlineSegment': 'string'
}

columns_to_keep = list(dtypes.keys())

print(f"Reading {csv_file_path}...")
df = pd.read_csv(csv_file_path, usecols=columns_to_keep, dtype=dtypes)

print(f"Writing {parquet_file_path}...")
df.to_parquet(parquet_file_path, engine='pyarrow', compression='snappy')

print("Conversion complete.")
