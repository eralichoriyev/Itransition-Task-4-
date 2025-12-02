import pandas as pd
df = pd.read_parquet("orders.parquet")
print(df.head(20))
print(df.dtypes)
print(df['unit_price'].head(10).tolist())