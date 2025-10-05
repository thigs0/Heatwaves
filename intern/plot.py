import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

hw = pd.read_csv("heatwave_ref.csv") #abre as ondas de calor
hw.time = pd.to_datetime(hw.time)
if  "Unnamed: 0" in hw.columns: hw = hw.drop(columns=["Unnamed: 0"])

def Linear_reg(df:pd.DataFrame) -> np.array:
    if len(df.columns) == 2:
        a,b = np.polyfit(df.iloc[:, 0], df.iloc[:, 1], 1)
        return np.array([a,b])
    else:
        raise("The dataframe need be only two columns")

def Mann_Kendall_Test(df):
        def sign(v):
            if (v>0):   return 1
            elif (v==0):return 0
            else:       return -1
        def p_value(s):
            if (s>0):   return (s-1)/np.std(np.array(df.iloc[:,1]))  
            elif (s==0):return 0
            else:       return (s+1)/np.std(np.array(df.iloc[:, 1]))
        s = 0
        for i in range(len(df)):
            for j in range(i, len(df)):
                s += sign(df.iloc[j,1] - df.iloc[i, 1])
        return (s, p_value(s)) 
        
#generate the graph with regression and save the data:
plt.style.use('ggplot')
years = hw.loc[:,'time'].dt.year.unique()
heatwave = [hw.loc[hw.time.dt.year == i, 'heatwave'].sum() for i in years]

fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(years, heatwave)
ax.set_ylabel("Ondas de calor")
ax.set_xlabel("Anos")
ax.set_title("Número de ondas de calor anual")
ax.set_xticks(years)
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
plt.savefig("Heatwave.png", dpi=300)
plt.close()


"""# Kendall
with open("kendall.csv", "w") as txt:
    p1,p2 = Mann_Kendall_Test(hw)
    txt.write(f"Para Heatwave temos {round(p1, 2)} e {round(p2, 2)}\n")
    p1,p2 = Mann_Kendall_Test(hw_day)
    txt.write(f"Para Heatwave contínua temos {round(p1, 2)} e {round(p2, 2)}")
"""
