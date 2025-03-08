"""
Calcula as ondas de calor por ano e seus tamanhos.
salva em um arquivo de saída .csv 

"""
from alive_progress import alive_bar
import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def heatwave_Dataset(ds:xr.Dataset, percent:xr.Dataset) -> pd.DataFrame: #gera um dataframe com o valor de da temperatura e a referênia
    historical = ds.sel(time = ds.time[ ((ds.time.dt.year > 1961) ) & (ds.time.dt.year <1991) ] ) #Filtra os dados < 1991 e > 1961
    data = ds.sel(time = ds.time[ ds.time.dt.year >=1991 ]) #Filtra o restante dos dados
    years = np.arange( data.time.dt.year[0].to_numpy().item(), data.time.dt.year[-1].to_numpy().item()+1 )#
    df = pd.DataFrame()
    df["time"] = data.time #dataframe de saída
    df[['tmax', 'ref', 'greater', 'heatwave']] = pd.NA

    #Calculo das ondas de calor
    year = years[0]

    print('gerando csv com dias mais quentes')
    with alive_bar( len(df.time) ) as bar:
        for i,date in enumerate(df['time']):
            x = data.sel(time=date).tmax
            y = percent.tmax.values[ ((percent.time.dt.month == date.month) & (percent.time.dt.day == date.day)) ].flatten() #valor do percentil no dia
            df.loc[i, 'tmax'] = x.to_numpy().item()
            df.loc[i, 'ref'] = y
            df.loc[i, 'greater'] = 1 if df.loc[i, 'tmax'] > df.loc[i, 'ref'] else 0
            bar()
    print('Gerando csv com as ondas de calor')
    #heatwave
    i = 0
    with alive_bar( len(df.time) ) as bar:
        while i < len(df.time)-3:
            df.loc[i, 'heatwave'] = 1 if df.loc[i:i+2, 'greater'].sum() == 3 else 0
            if df.loc[i, 'heatwave'] == 1:
                i+=3
            else:
                i+=1
            bar()

    return df

def Season_heatwave(df:pd.DataFrame)->None:
    """Recebe um dataframe com 1 se o dia teve onda de calor e 0 se não. Assim criar um novo dataframe com as ondas d calor
    separadas por estação"""
    hw = pd.DataFrame(columns=["time","1","2","3","4"]) #dataframe com resultados
    hw["time"] = np.arange(df["time"][0].year, df["time"][len(df)-1].year+1) # each year
    
    for i,j in enumerate(hw["time"][:]):
        #dez jan fev
        t = df[((df["time"].dt.year == j-1)&(df["time"].dt.month==12)|(df["time"].dt.year==j)&(df["time"].dt.month <= 2))] #data avaliada
        hw["1"][i] = np.sum(t["heatwave"])

        #mar abril maio
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=3)&(df["time"].dt.month <= 5)) ]
        hw["2"][i] = np.sum(t["heatwave"])

        #jun jul ago
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=6)&(df["time"].dt.month <= 8)) ]
        hw["3"][i] = np.sum(t["heatwave"])

        #set out nov
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=9)&(df["time"].dt.month <= 11)) ]
        hw["4"][i] = np.sum(t["heatwave"])

    
    hw.to_csv("season_heatwave.csv", index=False)

def main(tmax):
    #tmax é o nc de teperatura que iremos avaliar
    tmax = xr.open_dataset(tmax)
    tmax = tmax.sel(time = tmax.time[tmax.time.dt.year > 1990])
    time = pd.to_datetime(tmax.time.values)
    percent = xr.open_dataset("percentmax.nc")

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #1 se é um dia de início de onda de calor, 0 se não
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("os seguintes anos estão sendo considerados:")
    print(years)
    hw = np.zeros(years.size) #Will save the heatwave
    season = np.zeros((4, years.size))
    hw_cont = np.zeros(years.size)

    df = heatwave_Dataset(tmax, percent) 
    Season_heatwave(df)
    df.to_csv("tmax_ref.csv", index=False)

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
