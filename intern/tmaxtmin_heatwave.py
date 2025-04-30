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

def heatwave_Dataset(tmax:xr.Dataset, tmin:xr.Dataset, percentmax:xr.Dataset, percentmin:xr.Dataset) -> xr.Dataset: #gera um dataframe com o valor de da temperatura e a referênia
    tmax = tmax.where(tmax.time.dt.year > 1990, drop=True)
    tmin = tmin.where(tmin.time.dt.year > 1990, drop=True)
    #tmax = tmax.sel(time=tmax.time.dt.year >1990)

    tmax = tmax['tmax'] if isinstance(tmax, xr.Dataset) else tmax
    tmin = tmin['tmin'] if isinstance(tmin, xr.Dataset) else tmin
    percentmax = percentmax['tmax'] if isinstance(percentmax, xr.Dataset) else percentmax
    percentmin = percentmin['tmin'] if isinstance(percentmin, xr.Dataset) else percentmin

    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )#
    #rename coords of tmax, tmin, percentmax and percentmin 
    if "latitude" in tmax.coords:
        ds = tmax.rename({"latitude": "lat"})
    if "longitude" in tmax.coords:
        ds = tmax.rename({"longitude": "lon"})
    if "latitude" in tmin.coords:
        ds = tmin.rename({"latitude": "lat"})
    if "longitude" in tmin.coords:
        ds = tmin.rename({"longitude": "lon"})
    if "latitude" in percentmax.coords:
        ds = percentmax.rename({"latitude": "lat"})
    if "longitude" in percentmin.coords:
        ds = percentmax.rename({"longitude": "lon"})
    if "latitude" in percentmax.coords:
        ds = percentmin.rename({"latitude": "lat"})
    if "longitude" in percentmin.coords:
        ds = percentmin.rename({"longitude": "lon"})

    # Adiciona o dayofyear como coordenada em percentmax
    percentmax = percentmax.assign_coords(dayofyear=percentmax.time.dt.dayofyear)
    percent_daily = percentmax.groupby('dayofyear').mean(dim='time')
    percent_daily = percent_daily.assign_coords(dayofyear=percent_daily['dayofyear'])
    data_dayofyear = tmax.time.dt.dayofyear
    percentmax_expanded = percent_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmax_expanded = percentmax_expanded.assign_coords(time=tmax.time)
    percentmax = percentmax_expanded

    # Adiciona o dayofyear como coordenada em percentmax
    percentmin = percentmin.assign_coords(dayofyear=percentmin.time.dt.dayofyear)
    percent_daily = percentmin.groupby('dayofyear').mean(dim='time')
    percent_daily = percent_daily.assign_coords(dayofyear=percent_daily['dayofyear'])
    data_dayofyear = tmin.time.dt.dayofyear
    percentmin_expanded = percent_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmin_expanded = percentmin_expanded.assign_coords(time=tmin.time)
    percentmin = percentmin_expanded

    percentmax = percentmax.broadcast_like(tmax)
    percentmin = percentmin.broadcast_like(tmin)

    #Calcule heatwave
    year = years[0]
    print("Calculating the heatwaves")
    greater = ((tmax > percentmax)&(tmin > percentmin)).astype(int)
    rolling_sum = greater.rolling(time=3).sum()
    heatwave_flag = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)
    
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

    ref_max = percentmax.broadcast_like(tmax)
    ref_min = percentmin.broadcast_like(tmin)
    #out netcdf
    out_ds = xr.Dataset({
        'tmax': tmax,
        'tmin': tmin,
        'refmin': ref_min,
        'refmax': ref_max,
        'greater': greater,
        'heatwave': heatwave_events,
    })
    out_ds.to_dataframe().reset_index().to_csv("tmax_ref.csv", index=False)
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
            result[s].append(season_data.sum().item())

    # Criação do novo Dataset de estações
    season_ds = xr.Dataset({
        "DJF": (("year",), result["1"]),
        "MAM": (("year",), result["2"]),
        "JJA": (("year",), result["3"]),
        "SON": (("year",), result["4"]),
    }, coords={"year": result["year"]})

    season_ds.to_dataframe().reset_index().to_csv("season_heatwave.csv", index=False)

def main(tmax:xr.Dataset, tmin:xr.Dataset, percentmax:xr.Dataset, percentmin:xr.Dataset):
    #tmax é o nc de teperatura que iremos avaliar
    tmax = xr.open_dataset(tmax)
    tmin = xr.open_dataset(tmin)

    percentmax = xr.open_dataset('percentmax.nc')
    percentmin = xr.open_dataset('percentmin.nc')
    time = pd.to_datetime(tmax.time.values)

    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("The Heatwaves are of these years:")
    print(years)

    ds = heatwave_Dataset(tmax, tmin, percentmax, percentmin) 
    Season_heatwave(ds.heatwave)

if __name__ == "__main__":
    param1 = sys.argv[1] #tmax netcdf
    param2 = sys.argv[2] #tmin netcdf
    param3 = sys.argv[3] #percentmax
    param4 = sys.argv[4] #percentmin

    main(param1, param2, param3, param4)
