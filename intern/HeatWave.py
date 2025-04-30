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

import xarray as xr
import numpy as np

import xarray as xr

def heatwave_Dataset(ds: xr.Dataset, percent: xr.Dataset) -> xr.Dataset:
    # Ajusta nomes das coordenadas
    if "latitude" in ds.coords:
        ds = ds.rename({"latitude": "lat"})
    if "longitude" in ds.coords:
        ds = ds.rename({"longitude": "lon"})

    # Separa os dados históricos e atuais

    historical = ds.sel(time=(ds.time.dt.year > 1961) & (ds.time.dt.year < 1991))
    data = ds.where(ds.time.dt.year >= 1991, drop=True)
    data = ds.sel(time=ds.time.dt.year >= 1991)
    
    # Agrupa percentis por dia do ano
    percent_daily = percent.groupby('time.dayofyear').mean()

    # Extrai o dia do ano dos dados atuais
    data_dayofyear = data.time.dt.dayofyear

    # Seleciona o percentil correspondente a cada dia do ano
    ref_values = percent_daily.sel(dayofyear=data_dayofyear, method='nearest')

    # Garante que ref_base tenha apenas dimensão time
    ref_base = ref_values['tmax'] if isinstance(ref_values, xr.Dataset) else ref_values

    # Alinha a coordenada de tempo com o dataset de dados
    ref_base = ref_base.assign_coords(time=data.time)

    # Faz broadcast automático para lat/lon/time
    ref_broadcasted = ref_base.broadcast_like(data.tmax)

    # Comparação: dias com tmax acima do percentil
    greater = (data.tmax > ref_broadcasted).astype(int)

    # Rolling de 3 dias
    rolling_sum = greater.rolling(time=3).sum()

    heatwave_raw = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)

    # Cria máscara para registrar apenas o 1º dia e pular os 2 seguintes
    heatwave_events = heatwave_raw.copy(deep=True)
    heatwave_events[:] = 0

    i = 0
    while i < len(heatwave_raw.time):
        if heatwave_raw.isel(time=i):
            heatwave_events[i] = 1  # marca início do evento
            i += 3  # pula os próximos 2 dias (total 3 dias por evento)
        else:
            i += 1

    # Heatwave: 3 dias consecutivos acima do percentil
    heatwave_flag = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)

    # Cria o Dataset de saída
    out_ds = xr.Dataset({
        'tmax': data.tmax,
        'ref': ref_broadcasted,
        'greater': greater,
        'heatwave': heatwave_events,
    })

    return out_ds


def Season_heatwave(ds: xr.Dataset) -> xr.Dataset:
    """Recebe um Dataset com a variável 'heatwave' binária e retorna um novo Dataset com soma por estação."""

    years = np.arange(ds.time.dt.year.min().item(), ds.time.dt.year.max().item() + 1)
    seasons = {
        '1': ((ds.time.dt.month == 12) | (ds.time.dt.month <= 2)),
        '2': ((ds.time.dt.month >= 3) & (ds.time.dt.month <= 5)),
        '3': ((ds.time.dt.month >= 6) & (ds.time.dt.month <= 8)),
        '4': ((ds.time.dt.month >= 9) & (ds.time.dt.month <= 11)),
    }

    # Criação de array de resultado
    result = {season: [] for season in seasons}
    result["year"] = []

    for year in years:
        result["year"].append(year)
        for s, condition in seasons.items():
            if s == '1':
                # Dezembro do ano anterior + Jan/Fev do ano atual
                season_data = ds.sel(
                    time=(((ds.time.dt.year == year - 1) & (ds.time.dt.month == 12)) |
                          ((ds.time.dt.year == year) & (ds.time.dt.month <= 2)))
                )
            else:
                season_data = ds.sel(time=(ds.time.dt.year == year) & condition, method="nearest")
            result[s].append(season_data.heatwave.sum().item())

    # Criação do novo Dataset de estações
    season_ds = xr.Dataset({
        "DJF": (("year",), result["1"]),
        "MAM": (("year",), result["2"]),
        "JJA": (("year",), result["3"]),
        "SON": (("year",), result["4"]),
    }, coords={"year": result["year"]})

    season_ds.to_dataframe().reset_index().to_csv("season_heatwave.csv", index=False)


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
    print("Heatwave data are about these dates:")
    print(years)
    hw = np.zeros(years.size) #Will save the heatwave
    season = np.zeros((4, years.size))
    hw_cont = np.zeros(years.size)

    df = heatwave_Dataset(tmax, percent) 
    Season_heatwave(df)

    df.to_dataframe().reset_index().to_csv("tmax_ref.csv", index=False)

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
