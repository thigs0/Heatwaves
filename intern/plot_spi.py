import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ipywidgets as widgets
from scipy.stats import norm

ds = xr.open_dataset("spi.nc")
spi = ds.__xarray_dataarray_variable__.values[ds.time.dt.year >= 1990]
time = ds.time.values[ds.time.dt.year >= 1990]
plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(16, 9))
t = 1
for i,j in enumerate(spi):
    
    if j.item() >0:
        ax.scatter(time[i], j.item(), color="blue")
    else:
        ax.scatter(time[i], j.item(), color="red")
ax.set_ylabel('SPI')
ax.set_title('SPI mensal para campinas')
ax.set_ylim([-2,2])
ax.axhline(y=-0.5, color='black', linestyle='--', linewidth=2)
plt.savefig("spi.png")

plt.close()
plt.style.use('ggplot')
figManager = plt.get_current_fig_manager()

fig, ax = plt.subplots(figsize=(16, 9))
df = pd.read_csv("dados/Heatwave.csv")
ax.plot(df["time"], df["HeatWave"])
ax.set_ylabel("Ondas de calor")
ax.set_xlabel("Anos")
ax.set_title("Número de ondas de calor anual")
fig.tight_layout()
plt.savefig("Heatwave.png", dpi=300)
plt.close()

plt.style.use('ggplot')
figManager = plt.get_current_fig_manager()

fig, ax = plt.subplots(figsize=(16, 9))
df = pd.read_csv("Heatwaves_days.csv")
ax.plot(df["time"], df["Heatwave_days"])
ax.set_ylabel("Máximo de dias contínuos com onda de calor")
ax.set_title("Maior período contínuo com ondas de calor em dias")
ax.set_xlabel("Anos")
fig.tight_layout()
plt.savefig("Heatwave_day.png", dpi=300)
plt.close()



plt.style.use('ggplot')
df_05 = pd.read_csv("dados/cdh_-05.csv")
df = pd.read_csv("Heatwave.csv")
df_05["time"] = pd.to_datetime(df_05["time"])

cdh_05= np.zeros(33)
t = np.zeros(33)
for i in range(len(df)):
    cdh_05[i] = np.sum( df_05["cdh"][ df_05["time"].dt.year == df["time"][0]+i ])
    t[i] = df["time"][0]+i

plt.plot(t, cdh_05, label="spi abaixo de  -0.5", color="r")
plt.ylabel("cdh")
plt.legend()
plt.xlabel("Years")
fig.tight_layout()
plt.savefig("cdh.png", dpi=300)
plt.close()

plt.style.use('ggplot')
df = pd.read_csv("Heatwaves_complete.csv")
df["time"] = pd.to_datetime(df["time"])
fig, axs = plt.subplots(2, 2)

cdh_1 = np.zeros(33)
cdh_2 = np.zeros(33)
cdh_3 = np.zeros(33)
cdh_4 = np.zeros(33)
t = np.zeros(33)
for i in range(33):
        if i != 0:
            cdh_1[i] = np.sum( 
            df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i-1 ) & (df["time"].dt.month ==12))]
                         ) + np.sum(
            df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==1))]
            ) + np.sum(
            df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==2))]
            )

        cdh_2[i] = np.sum( 
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==3))]
                     ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==4))]
        ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==5))]
        )
  
        cdh_3[i] = np.sum( 
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==6))]
                     ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==7))]
        ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==8))]
        )
  
        cdh_4[i] = np.sum( 
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==9))]
                     ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==10))]
        ) + np.sum(
        df["cdh"][ np.array(( df["time"].dt.year == df["time"][0].year+i ) & (df["time"].dt.month ==11))]
        )
        t[i] = df["time"][0].year+i

axs[0,0].plot(t[1:], cdh_1[1:], color="r",label="Dez, Jan, Fev")
axs[0,0].legend()
axs[0,0].set_ylim([-1,15])

axs[0,1].plot(t, cdh_2, color="r",label="Mar, Abr, Mai")
axs[0,1].legend()
axs[0,1].set_ylim([-1,15])

axs[1,0].plot(t, cdh_3, color="b",label="Jun, Jul, Ago")
axs[1,0].legend()
axs[1,0].set_ylim([-1,15])

axs[1,1].plot(t, cdh_4, color="b",label="Set, Out, Nov")
axs[1,1].legend()
axs[1,1].set_ylim([-1,15])

fig.suptitle("Quantidade de ondas de calor", fontsize="x-large")
fig.tight_layout()
plt.legend()
plt.savefig("heatwave_season_day.png", dpi=300)
plt.close()

#Season
plt.style.use('ggplot')
df = pd.read_csv("season.csv")
fig, axs = plt.subplots(2, 2)

fig.suptitle("Maior quantidade de dias contínuos em uma onda de calor", fontsize="x-large")
axs[0,0].plot(df["time"][1:], df["1"][1:], color="r",label="Dez, Jan, Fev")
axs[0,0].legend()
axs[0,0].set_ylim([-1,23])

axs[0,1].plot(df["time"], df["2"], color="r",label="Mar, Abr, Mai")
axs[0,1].legend()
axs[0,1].set_ylim([-1,23])

axs[1,0].plot(df["time"], df["3"], color="b",label="Jun, Jul, Ago")
axs[1,0].legend()
axs[1,0].set_ylim([-1,23])

axs[1,1].plot(df["time"], df["4"], color="b",label="Set, Out, Nov")
axs[1,1].legend()
axs[1,1].set_ylim([-1,23])

fig.tight_layout()
plt.legend()
plt.savefig("season.png", dpi=300)
plt.close()


