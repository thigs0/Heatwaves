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

def heatwave_Dataset(tmax: xr.Dataset, tmin: xr.Dataset, percentmax: xr.Dataset, percentmin: xr.Dataset) -> xr.Dataset:
    # Filtra os anos a partir de 1991
    tmax = tmax.where(tmax.time.dt.year > 1990, drop=True)
    tmin = tmin.where(tmin.time.dt.year > 1990, drop=True)

    # Seleciona as variáveis se vierem como Dataset
    tmax = tmax['tmax'] if isinstance(tmax, xr.Dataset) else tmax
    tmin = tmin['tmin'] if isinstance(tmin, xr.Dataset) else tmin
    percentmax = percentmax['tmax'] if isinstance(percentmax, xr.Dataset) else percentmax
    percentmin = percentmin['tmin'] if isinstance(percentmin, xr.Dataset) else percentmin

    # Renomeia coordenadas se necessário
    for var in [tmax, tmin, percentmax, percentmin]:
        if "latitude" in var.coords:
            var = var.rename({"latitude": "lat"})
        if "longitude" in var.coords:
            var = var.rename({"longitude": "lon"})

    # Alinha percentmax com tmax
    percentmax = percentmax.assign_coords(dayofyear=percentmax.time.dt.dayofyear)
    percentmax_daily = percentmax.groupby('dayofyear').mean(dim='time')
    percentmax_daily = percentmax_daily.assign_coords(dayofyear=percentmax_daily['dayofyear'])
    data_dayofyear = tmax.time.dt.dayofyear
    percentmax_expanded = percentmax_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmax_expanded = percentmax_expanded.assign_coords(time=tmax.time)
    percentmax = percentmax_expanded

    # Alinha percentmin com tmin
    percentmin = percentmin.assign_coords(dayofyear=percentmin.time.dt.dayofyear)
    percentmin_daily = percentmin.groupby('dayofyear').mean(dim='time')
    percentmin_daily = percentmin_daily.assign_coords(dayofyear=percentmin_daily['dayofyear'])
    percentmin_expanded = percentmin_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmin_expanded = percentmin_expanded.assign_coords(time=tmin.time)
    percentmin = percentmin_expanded

    # Condição de calor: dias que excedem os percentis
    greater_both = ((tmax > percentmax) & (tmin > percentmin)).astype(int)

    
    start_heatwave = (greater_both.rolling(time=3, min_periods=3).sum() >= 3)
    # Inicializa heatwave
    heatwave = xr.zeros_like(greater_both)
    
    for lat in tmax.lat.values:
        for lon in tmax.lon.values:
            g = greater_both.sel(lat=lat, lon=lon)
            s = start_heatwave.sel(lat=lat, lon=lon)
            h = xr.zeros_like(g)

            in_wave = False
            for t in range(g.sizes['time']):
                if not in_wave and s.isel(time=t).item():
                    h[t] = 1
                    in_wave = True
                elif in_wave and g.isel(time=t).item() == 0:
                    in_wave = False

            heatwave.loc[dict(lat=lat, lon=lon)] = h

    # Cria dataset de saída
    out_ds = xr.Dataset({
        'tmax': tmax,
        'tmin': tmin,
        'refmax': percentmax,
        'refmin': percentmin,
        'greater': greater_both,
        'heatwave': heatwave
    })

    # Exporta para CSV (opcional)
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
            result[s].append(season_data.heatwave.sum().item())

    # Criação do novo Dataset de estações
    season_ds = xr.Dataset({
        "DJF": (("year",), result["1"]),
        "MAM": (("year",), result["2"]),
        "JJA": (("year",), result["3"]),
        "SON": (("year",), result["4"]),
    }, coords={"year": result["year"]})

    season_ds.to_dataframe().reset_index().to_csv("season_heatwave.csv", index=False)

def main(tmax:xr.Dataset, tmin:xr.Dataset, maxpercent:xr.Dataset, minpercent:xr.Dataset):
    #tmax é o nc de teperatura que iremos avaliar
    tmax, tmin = xr.open_dataset(tmax), xr.open_dataset(tmin)
    tmax, tmin = tmax.sel(time = tmax.time[tmax.time.dt.year > 1990]), tmin.sel(time = tmin.time[tmin.time.dt.year > 1990])
    time = pd.to_datetime(tmax.time.values)
    maxpercent, minpercent = xr.open_dataset(maxpercent), xr.open_dataset(minpercent)

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #1 se é um dia de início de onda de calor, 0 se não
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("os seguintes anos estão sendo considerados:")
    print(years)
    hw = np.zeros(years.size) #Will save the heatwave

    df = heatwave_Dataset(tmax,tmin, maxpercent, minpercent) 
    Season_heatwave(df)

if __name__ == "__main__":
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    param3 = sys.argv[3]
    param4 = sys.argv[4]

    main(param1, param2, param3, param4)
