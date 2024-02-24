import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

hw = pd.read_csv("Season.csv") #abre as ondas de calor
hw = hw.drop(columns=["Unnamed: 0"])

def Linear_reg(df:pd.DataFrame) -> np.array:
    if len(df.columns) == 2:
        a,b = np.polyfit(df.iloc[:, 0], df.iloc[:, 1], 1)
        return np.array([a,b])
    else:
        raise("O dataframe precisa ter somente duas colunas")

def Mann_Kendall_Test(df):
        def sign(v):
            if (v>0):
                return 1
            elif (v==0):
                return 0
            else:
                return -1
        def p_value(s):
            if (s>0):
                return (s-1)/np.std(np.array(df.iloc[:,1]))  
            elif (s==0):
                return 0
            else:
                return (s+1)/np.std(np.array(df.iloc[:, 1]))
        s = 0
        for i in range(len(df)):
            for j in range(i, len(df)):
                s += sign(df.iloc[j,1] - df.iloc[i, 1])
        return (s, p_value(s)) 
        
#Gera os gráficos com regressão e salva os dados:

plt.style.use('ggplot')
df = pd.read_csv("season.csv")
fig, axs = plt.subplots(2, 2)

fig.suptitle("Maior quantidade de dias contínuos em uma onda de calor", fontsize="x-large")
axs[0,0].plot(df["time"][1:], df["1"][1:], color="r",label="Dez, Jan, Fev")
a,b = Linear_reg(df["1"])
vec = a*df["1"] + b*np.ones(len(df["1"]))
axs[0,0].plot(df["1"], vec)
axs[0,0].legend()
axs[0,0].set_ylim([-1,23])

a,b = Linear_reg(df["2"])
vec = a*df["2"] + b*np.ones(len(df["2"]))
axs[0,1].plot(df["2"], vec)
axs[0,1].plot(df["time"], df["2"], color="r",label="Mar, Abr, Mai")
axs[0,1].legend()
axs[0,1].set_ylim([-1,23])

a,b = Linear_reg(df["3"])
vec = a*df["3"] + b*np.ones(len(df["3"]))
axs[1,0].plot(df["3"], vec)
axs[1,0].plot(df["time"], df["3"], color="b",label="Jun, Jul, Ago")
axs[1,0].legend()
axs[1,0].set_ylim([-1,23])

a,b = Linear_reg(df["4"])
vec = a*df["4"] + b*np.ones(len(df["4"]))
axs[1,0].plot(df["4"], vec)
axs[1,1].plot(df["time"], df["4"], color="b",label="Set, Out, Nov")
axs[1,1].legend()
axs[1,1].set_ylim([-1,23])

fig.tight_layout()
plt.legend()
plt.savefig("season_linear.png", dpi=300)
plt.close()

# Kendall
with open("season_kendall.csv", "w") as txt:
    p1,p2 = Mann_Kendall_Test(hw["1"])
    txt.write(f"Para Heatwave Nov,Dez, Jan temos {round(p1, 2)} e {round(p2, 2)}\n")
    p1,p2 = Mann_Kendall_Test(hw["2"])
    txt.write(f"Para Heatwave Fev,Mar, Abr temos {round(p1, 2)} e {round(p2, 2)}\n")
    p1,p2 = Mann_Kendall_Test(hw["3"])
    txt.write(f"Para Heatwave Mai, Jun, Jul temos {round(p1, 2)} e {round(p2, 2)}\n")
    p1,p2 = Mann_Kendall_Test(hw["4"])
    txt.write(f"Para Heatwave Ago, Set, Out temos {round(p1, 2)} e {round(p2, 2)}\n")
