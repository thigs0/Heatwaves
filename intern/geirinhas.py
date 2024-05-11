"""
Este código pega o percentil de temperatura de referência e o índice de precipitação SPI com o maior valor de SPI para cada mês.
 
"""

#Temos:
#percent.nc com o percentil 90 de cada dia do ano
#spi.nc é o maior valor de SPI para cada mês do ano
#pr.nc é o período que avaliamos a onda de calor com precipitação


import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def main(tmax, spi_param, nome):
    #t é o nc de teperatura que iremos avaliar

    spi = xr.open_dataset("spi.nc")
    spi = spi.rename({"__xarray_dataarray_variable__":"spi"})
    tmax = xr.open_dataset(tmax)
    percent = xr.open_dataset("percent.nc")
    n = len(tmax.time.values)
    i = y = 0

    r = np.zeros(n) #1 se é um dia de onda de calor, 0 se não
    lat = np.zeros(n)
    lon = np.zeros(n)
    time = pd.to_datetime(tmax.time.values) 
    spi_param = float(spi_param) 
    spi_mes = 1

    for j,la in enumerate(tmax.lat.values): #Percorre a latitude
        for k, lo in enumerate(tmax.lat.values): #Percorre a longitude
            while i < n-3:
                tpercent = 0
                y = 0 #Variável tempórária
                for l in range(3): #avalia em 3 dias seguidos
                    x = time[i] + pd.DateOffset(day=l)
                    y = percent.tmax.values[ ((percent.time.dt.month == x.month) & (percent.time.dt.day == x.day)) ].flatten() #valor do percentil no dia
                    tpercent += y < tmax.tmax.values[i+l]
                if tpercent == 3: #Se o percentil é igual a temperatura para os 3 dias, temos uma onda de calor
                    tpercent = np.zeros(spi_mes)
                    # Coleta o dado de cada mês e cacula o índice
                    if time[i].year != time[0].year : #Se o ano não é o inicial
                        for l in range(1, spi_mes+1):
                            x = time[i] - pd.DateOffset(month=l-1)
                            tpercent[l-1] = spi.spi[ ((spi["time"].dt.month == x.month) & (spi["time"].dt.year == x.year)) ].item()
                        if np.sum( tpercent <= (np.ones(spi_mes)*spi_param) ) == np.size(tpercent): #todos valores são verdadeiros 
                            r[i] = 1
                        else:
                            pass
                    else: # é o ano inicial
                        if time[i].month < spi_mes: # se temos meses suficientes para avaliar o spi
                            pass
                        else:
                            for l in range(1, spi_mes+1):
                                x = time[i] - pd.DateOffset(month=l-1)
                                tpercent[l-1] = spi.spi[ ((spi["time"].dt.month == x.month) & (spi["time"].dt.year == x.year)) ].item()
                            if np.sum( tpercent <= (np.ones(spi_mes)*spi_param) ) == np.size(tpercent): #todos valores são verdadeiros 
                                r[i] = 1
                            else:
                                pass
                    i +=3
                else:# Se o percentil não é maior que a temperatura e não chegamos no final
                    i += 1

    df = pd.DataFrame()
    df["cdh"] = r
    df["time"] = time 
    df.to_csv(f"../{nome}")

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    parametro2 = sys.argv[2]

    parametro3 = sys.argv[3]

    # Chama a função com os parâmetros fornecidos
    print(main(parametro1, parametro2, parametro3))
