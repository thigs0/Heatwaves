import pandas as pd
import numpy as np

df = pd.read_csv("heatwave_ref.csv")
df.time = pd.to_datetime(df.time)
df[['tmean_heatwave', 'tlast30', 'EHF', 'EHI_sig', 'EHI_acc']] = np.nan

print("Calculate the average temperature at each heatwave")
for i,j in enumerate(df['heatwave']):#calcula o EHI_sig
    if j == 1:
        df.loc[i, 'heatwave_heatwave'] = df.loc[i:i+2, 'tmax'].sum()/3
        df.loc[i, 'EHI_sig'] = df.loc[i, 'tmean_heatwave'] - np.percentile( df.loc[ df.time.dt.year == 2020, 'ref' ], 90 )

print("Calculating the mean temperature each month")
for i,j in enumerate(df['heatwave']):#calcula o EHI_acc
    if j == 1:
        df.loc[i, 'tlast30'] = df.loc[i-30:i, 'tmax'].sum()/30
        df.loc[i, 'EHI_acc'] = df.loc[i, 'tmean_heatwave'] - df.loc[i, 'tlast30']


for i in np.arange(len(df.time)):
    df.loc[i, 'EHF'] = df.loc[i, 'EHI_sig'] * np.nanmax( [df.loc[i, 'EHI_acc'], 1] )

df.to_csv("heatwave_ref.csv", index=False)

