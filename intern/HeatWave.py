"""
Calcula as ondas de calor por ano e seus tamanhos.
salva em um arquivo de saída .csv 

"""

import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def Season_heatwave(df:pd.DataFrame)->None:
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

def main(tmax):
    #tmax é o nc de teperatura que iremos avaliar
    tmax = xr.open_dataset(tmax)
    time = pd.to_datetime(tmax.time.values)
    percent = xr.open_dataset("percent.nc")

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #1 se é um dia de início de onda de calor, 0 se não
    years = np.arange( time.year[0], time.year[n-1]+1 )
    hw = np.zeros(years.size)
    season = np.zeros((4, years.size))
    hw_cont = np.zeros(years.size)

    #Calculo das ondas de calor
    year = years[0]
    while i < n-3: #Enquanto não estamos no final
        tpercent = 0
        if (time[i] + pd.DateOffset(day=3)).year != year: #Restringe as ondas de calor no mesmo ano, sem passar para outro
            i+=3
            year+=1
        else:
            for k in range(3): 
                x = time[i] + pd.DateOffset(day=k)
                y = percent.tmax.values[ ((percent.time.dt.month == x.month) & (percent.time.dt.day == x.day)) ].flatten() #valor do percentil no dia
                tpercent += y < tmax.tmax.values[i+k] #compara o percentil dos dois dias 
            if tpercent == 3: #Se todos os 3 dias estão acima do percentil
                r[i] = 1
                i+=3
            else:
                i+=1
        
    #calcula as ondas de calor por ano
    for j,y in enumerate(years):
        hw[j] = np.sum( r[time.year == y] ) #soma todas as ondas de calor que ocorreram no ano y
    
    #Para cada ano, calcula a quantidade de ondas de calor
    for k, y in enumerate(years):
        date = tmax.tmax.values[ time.year == y ] #todos as datas do ano y
        i=0
        while i < date.size: #percorre os dias do ano y
            c=0
            while i < date.size and date[i] > percent.tmax.values[i]: # Enquanto o arquivo tem dados e temos uma onda de calor
                c+=1 #é um dia com heatwave
                i+=1 #pula um dia
            if c > hw_cont[k]: # se a onda atual é maior que a anterior para o mesmo ano
                hw_cont[k] = c
            i += 1

    #Para sazonalidade contínua
    for k, y in enumerate(years):
        if k != 0 :
            date = tmax.tmax.values[ (
                (time.year == y-1) & (time.month == 12) |
                (time.year == y) & (time.month ==1) |
                (time.year == y) & (time.month ==2)
            ) ].flatten() #todos as datas do ano y
            i=0

            while i < date.size: #percorre os dias do ano y
                c=0
                while i < date.size and date[i] > percent.tmax.values[i]: # Enquanto o arquivo tem dados e temos uma onda de calor
                    c+=1 #é um dia com heatwave
                    i+=1 #pula um dia
                if c > season[0][k]: # se a onda atual é maior que a anterior para o mesmo ano
                    season[0][k] = c
                i += 1


        for zi, z in enumerate((3,6,9)):
            date = tmax.tmax.values[ (
                (time.year == y-1) & (time.month ==z) |
                (time.year == y) & (time.month ==z+1) |
                (time.year == y) & (time.month == z+2)
            ) ].flatten() #todos as datas do ano y
            i=0

            while i < date.size: #percorre os dias do ano y
                c=0
                while i < date.size and date[i] > percent.tmax.values[i]: # Enquanto o arquivo tem dados e temos uma onda de calor
                    c+=1 #é um dia com heatwave
                    i+=1 #pula um dia
                if c > season[zi+1][k]: # se a onda atual é maior que a anterior para o mesmo ano
                    season[zi+1][k] = c
                i += 1


    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["HeatWave"] = hw[years > 1990]
    df.to_csv("Heatwave.csv")

    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["Heatwave_days"] = hw_cont[years > 1990]
    df.to_csv("Heatwaves_days.csv")
    
    df = pd.DataFrame()
    df["time"] = time[time.year > 1990]
    df["cdh"] = r[time.year > 1990]
    df.to_csv("Heatwaves_complete.csv")

    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["1"] = season[0][years > 1990]
    df["2"] = season[1][years > 1990]
    df["3"] = season[2][years > 1990]
    df["4"] = season[3][years > 1990]
    df.to_csv("season.csv")
    
    df = pd.read_csv("Heatwaves_complete.csv")
    df["time"] = pd.to_datetime(df["time"])
    df = df[ df["time"].dt.year >= 1991 ]
    Season_heatwave(df)

if __name__ == "__main__":
    parametro1 = sys.argv[1]

    main(parametro1)
