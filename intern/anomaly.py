import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("tmax_ref.csv")
df.time = pd.to_datetime(df.time)
df = df[ ~np.isnan(df.time) ]
df = df.fillna(0)

years = np.array(df.time.dt.year.unique())
years = years[ ~np.isnan(years) ]

#constrio

print('construindo gráfico da anomalia')
c = df[df.cummulative != 0] 
c = df.loc[: , ['time', 'cummulative']]
plt.scatter(c.time, c.cummulative, s=c.cummulative)
plt.xlabel('Data')
plt.title('Onda de calor registrada em cada data e sua anomalia')
plt.ylabel('Onda de calor')
plt.savefig('anomaly.png', dpi=300)

print('feito')
