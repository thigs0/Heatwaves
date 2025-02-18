import pandas as pd
import numpy as np

df = pd.read_csv('tmax_ref.csv')
df.time = pd.to_datetime(df.time)
df['cummulative'] = 0.0

print('Calculando o cummulative')
for i,j in enumerate(df['heatwave']):
    if j == 1:
        df.loc[i, 'cummulative'] = df.loc[i:i+2, 'tmax'].sum() - df.loc[i:i+2, 'ref'].sum()


df.to_csv('tmax_ref.csv', index=False)
