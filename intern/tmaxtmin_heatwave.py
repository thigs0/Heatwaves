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

def heatwave_Dataset(tmax:xr.Dataset, tmin:xr.Dataset, percentmax:xr.Dataset, percentmin:xr.Dataset) -> pd.DataFrame: #gera um dataframe com o valor de da temperatura e a referênia
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )#
    df = pd.DataFrame()
    df["time"] = data.time #dataframe de saída
    df[['tmax', 'ref_tmax', 'ref_tmin', 'greater', 'heatwave']] = pd.NA


    #Calculo das ondas de calor
    year = years[0]

    print('gerando csv com dias mais quentes')
    with alive_bar( len(df.time) ) as bar:
        for i,date in enumerate(df['time']):
            xmax = tmax.sel(time=date).tmax
            xmin = tmin.sel(time=date).tmin
            ymax = percentmax.tmax.values[ ((percentmax.time.dt.month == date.month) & (percentmax.time.dt.day == date.day)) ].flatten() #valor do percentil no dia
            ymin = percentmin.tmin.values[ ((percentmin.time.dt.month == date.month) & (percentmin.time.dt.day == date.day)) ].flatten() #valor do percentil no dia
            df.loc[i, 'tmax'] = xmax.to_numpy().item()
            df.loc[i, 'tmin'] = xmin.to_numpy().item()
            df.loc[i, 'ref_max'] = ymax
            df.loc[i, 'ref_min'] = ymin
            df.loc[i, 'greater'] = 1 if df.loc[i, 'tmax'] > df.loc[i, 'ref_tmax'] and  df.loc[i, 'tmin'] > df.loc[i, 'ref_tmin'] else 0
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

def Season_heatwave(df:pd.DataFrame) -> None:
    """Recebe um dataframe com 1 se o dia teve onda de calor e 0 se não. Assim criar um novo dataframe com as ondas d calor
    separadas por estação"""
    hw = pd.DataFrame(columns=["time","1","2","3","4"]) #dataframe com resultados
    hw["time"] = np.arange(df["time"][0].year, df["time"][len(df)-1].year+1) # each year
    
    for i,j in enumerate(hw["time"][:]):
        #dez jan fev
        t = df[((df["time"].dt.year == j-1)&(df["time"].dt.month==12)|(df["time"].dt.year==j)&(df["time"].dt.month <= 2))] #data avaliada
        hw["1"][i] = np.sum(t["cdh"])

        #mar abril maio
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=3)&(df["time"].dt.month <= 5)) ]
        hw["2"][i] = np.sum(t["cdh"])

        #jun jul ago
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=6)&(df["time"].dt.month <= 8)) ]
        hw["3"][i] = np.sum(t["cdh"])

        #set out nov
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=9)&(df["time"].dt.month <= 11)) ]
        hw["4"][i] = np.sum(t["cdh"])

    
    hw.to_csv("season_heatwave.csv")

def main(tmax, tmin, percentmax, percentmin):
    #tmax é o nc de teperatura que iremos avaliar
    tmax = xr.open_dataset(tmax)
    tmax = tmax.sel(time = tmax.time[tmax.time.dt.year > 1990])
    tmin = xr.open_dataset(tmin)
    tmin = tmin.sel(time = tmin.time[tmin.time.dt.year > 1990])

    percentmax = xr.open_dataset(percentmax)
    percentmin = xr.open_dataset(percentmin)

    time = pd.to_datetime(tmax.time.values)

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #1 se é um dia de início de onda de calor, 0 se não
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("os seguintes anos estão sendo considerados:")
    print(years)

    df = heatwave_Dataset(tmax, tmin,percentmax, percentmin) 
    df.to_csv("tmax_ref.csv", index=False)

if __name__ == "__main__":
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    param3 = sys.argv[3]
    param4 = sys.argv[4]

    main(param1, param2, param3, param4)
