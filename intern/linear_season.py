import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def Linear_reg(df:pd.DataFrame) -> np.array:
    #retorna um vetor com dois parâmetros da regressão linear
    if len(df.columns) == 2:
        a,b = np.polyfit(df.iloc[:, 0], df.iloc[:, 1], 1)
        return np.array([a,b])
    else:
        raise("O dataframe precisa ter somente duas colunas")

def Mann_Kendall_Test(df:pd.DataFrame):
    """Retorna os parâmetros do teste de Mann Kendall"""

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
        
#gera os mesmos gráficos para heatwave e salva

plt.style.use('ggplot')
df = pd.read_csv("season_heatwave.csv")
fig, axs = plt.subplots(2, 2)

fig.suptitle("ondas de calor por estação", fontsize="x-large")
a,b = Linear_reg(df[["time", "1"]])
vec = a*df["time"] + b*np.ones(len(df["time"]))
axs[0,0].plot(df["time"][:], vec, label=f"Coeficiente angular {round(a, 2)}",color="black")
axs[0,0].plot(df["time"][1:], df["1"][1:], color="r",label="Dez, Jan, Fev")
axs[0,0].legend()
axs[0,0].set_ylim([-1,23])

a,b = Linear_reg(df[["time","2"]])
vec = a*df["time"] + b*np.ones(len(df["time"]))
axs[0,1].plot(df["time"][:], vec, label=f"Coeficiente angular {round(a, 2)}",color="black")
axs[0,1].plot(df["time"], df["2"], color="r",label="Mar, Abr, Mai")
axs[0,1].legend()
axs[0,1].set_ylim([-1,23])

a,b = Linear_reg(df[["time","3"]])
vec = a*df["time"] + b*np.ones(len(df["time"]))
axs[1,0].plot(df["time"][:], vec, label=f"Coeficiente angular {round(a, 2)}",color="black")
axs[1,0].plot(df["time"], df["3"], color="b",label="Jun, Jul, Ago")
axs[1,0].legend()
axs[1,0].set_ylim([-1,23])

a,b = Linear_reg(df[["time","4"]])
vec = a*df["time"] + b*np.ones(len(df["time"]))
axs[1,1].plot(df["time"][:], vec, label=f"Coeficiente angular {round(a, 2)}", color="black")
axs[1,1].plot(df["time"], df["4"], color="b",label="Set, Out, Nov")
axs[1,1].legend()
axs[1,1].set_ylim([-1,23])

fig.tight_layout()
plt.legend()
plt.savefig("season_heatwave_linear.png", dpi=300)
plt.close()

#witout linear
plt.style.use('ggplot')
df = pd.read_csv("season_heatwave.csv")
fig, axs = plt.subplots(2, 2)

fig.suptitle("ondas de calor por estação", fontsize="x-large")
axs[0,0].plot(df["time"][1:], df["1"][1:], color="r",label="Dez, Jan, Fev")
axs[0,0].legend()
axs[0,0].set_ylim([-1,23])

a,b = Linear_reg(df[["time","2"]])
axs[0,1].plot(df["time"], df["2"], color="r",label="Mar, Abr, Mai")
axs[0,1].legend()
axs[0,1].set_ylim([-1,23])

a,b = Linear_reg(df[["time","3"]])
axs[1,0].plot(df["time"], df["3"], color="b",label="Jun, Jul, Ago")
axs[1,0].legend()
axs[1,0].set_ylim([-1,23])

a,b = Linear_reg(df[["time","4"]])
axs[1,1].plot(df["time"], df["4"], color="b",label="Set, Out, Nov")
axs[1,1].legend()
axs[1,1].set_ylim([-1,23])

fig.tight_layout()
plt.legend()
plt.savefig("season_heatwave.png", dpi=300)
plt.close()



