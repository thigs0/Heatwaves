import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("heatwave_ref.csv")
df.time = pd.to_datetime(df.time)

years = df.time.dt.year.unique()
value = [ df.loc[ df.time.dt.year == i , 'EHF'].max() for i in df.time.dt.year.unique() ]

#plot
plt.style.use('ggplot')
fig, axs = plt.subplots(figsize=(16, 9))

axs.plot(years, value, label='EHF máxima por ano')
axs.set_xticks(years)
axs.set_xlabel("Anos")
axs.set_title("EHF máximo que ocorreu em cada ano")
axs.set_ylabel('EHF')
axs.tick_params(axis='x', rotation = 45)
fig.tight_layout()
plt.savefig("EHF.png", dpi=300)

