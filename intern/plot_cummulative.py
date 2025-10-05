import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("heatwave_ref.csv")
df.time = pd.to_datetime(df.time)
df = df[ ~np.isnan(df.time) ]
df = df.fillna(0)

years = np.array(df.time.dt.year.unique())
years = years[ ~np.isnan(years) ]
value = [ df.loc[ df.time.dt.year == i , 'cummulative'].sum()/df.loc[ df.time.dt.year == i , 'heatwave'].sum()  for i in years ]

#plot
plt.style.use('ggplot')
fig, axs = plt.subplots(figsize=(16, 9))

axs.plot(years, value, label='soma das anomalias')
axs.set_xticks(years)
axs.set_xlabel("Anos")
axs.set_title("Soma das anomalías de temperatura por ano dividido pelo número de ondas de calor")
axs.set_ylabel('Acumulado de anomalias')
axs.tick_params(axis='x', rotation = 45)
plt.savefig("cummulative.png", dpi=300)

print('construindo gráfico da anomalia')
c = df[df.cuumulative != 0] 
c = df.loc[: , ['time', 'cummulative']]
plt.scatter(c.time, c.cummulative, s=c.cummulative)
plt.xlabel('Data')
plt.title('Onda de calor registrada em cada data e sua anomalia')
plt.ylabel('Onda de calor')
plt.savefig('anomaly.png', dpi=300)

print('Done')
