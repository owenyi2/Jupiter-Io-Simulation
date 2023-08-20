import pandas as pd

df = pd.read_csv("simulation_log/down_sample.csv", index_col=0)
df1 = df.iloc[40000:60000]
df1.to_csv("down_sample 3.csv")