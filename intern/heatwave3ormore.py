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

def heatwave_Dataset(tmax: xr.Dataset, percentmax: xr.Dataset) -> xr.Dataset:
    # Filter the year after 1990
    tmax = tmax.where(tmax.time.dt.year > 1990, drop=True)

    tmax = tmax['tmax'] if isinstance(tmax, xr.Dataset) else tmax
    percentmax = percentmax['tmax'] if isinstance(percentmax, xr.Dataset) else percentmax

    # rename the coordenates if need
    for var in [tmax, percentmax]:
        if "latitude" in var.coords:
            var = var.rename({"latitude": "lat"})
        if "longitude" in var.coords:
            var = var.rename({"longitude": "lon"})

    # Align the percentmax com tmax
    percentmax = percentmax.assign_coords(dayofyear=percentmax.time.dt.dayofyear)
    percentmax_daily = percentmax.groupby('dayofyear').mean(dim='time')
    percentmax_daily = percentmax_daily.assign_coords(dayofyear=percentmax_daily['dayofyear'])
    data_dayofyear = tmax.time.dt.dayofyear
    percentmax_expanded = percentmax_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmax_expanded = percentmax_expanded.assign_coords(time=tmax.time)
    percentmax = percentmax_expanded

    # Heat condition: days that is bigger that percentile
    greater = (tmax > percentmax).astype(int)

    # start the heatwave: three consecutives days with true condition
    start_heatwave = greater.rolling(time=3, min_periods=3).sum() >= 3

    # start heatwave
    heatwave = xr.zeros_like(greater)

    # Apply the point logic (lat, lon)
    for lat in tmax.lat.values:
        for lon in tmax.lon.values:
            g = greater.sel(lat=lat, lon=lon)
            s = start_heatwave.sel(lat=lat, lon=lon)
            h = xr.zeros_like(g)
            in_wave = False
            for t in range(g.sizes['time']):
                if not in_wave and s.isel(time=t).item():
                    h[t] = 1
                    in_wave = True
                elif in_wave and g.isel(time=t).item() == 0:
                    in_wave = False
            # add result at array
            heatwave.loc[dict(lat=lat, lon=lon)] = h
    #create the output dataset
    out_ds = xr.Dataset({
        'tmax': tmax,
        'refmax': percentmax,
        'greater': greater,
        'heatwave': heatwave
    })

    # Exporta para CSV (opcional)
    out_ds.to_dataframe().reset_index().to_csv("heatwavw_ref.csv", index=False)
    return out_ds

def Season_heatwave(ds: xr.Dataset) -> None:
    """Need a dataset with a variable 'heatwave' binary and return a new dataset with sum per season."""

    years = np.arange(ds.time.dt.year.min().item(), ds.time.dt.year.max().item() + 1)
    seasons = {
        '1': ((ds.time.dt.month == 12) | (ds.time.dt.month <= 2)),
        '2': ((ds.time.dt.month >= 3) & (ds.time.dt.month <= 5)),
        '3': ((ds.time.dt.month >= 6) & (ds.time.dt.month <= 8)),
        '4': ((ds.time.dt.month >= 9) & (ds.time.dt.month <= 11)),
    }

    # Create the array result
    result = {season: [] for season in seasons}
    result["year"] = []
    for year in years:
        result["year"].append(year)
        for s, condition in seasons.items():
            if s == '1':
                # Dezember of last year + Jan/Fevb of current year
                season_data = ds.sel(
                    time=(((ds.time.dt.year == year - 1) & (ds.time.dt.month == 12)) |
                          ((ds.time.dt.year == year) & (ds.time.dt.month <= 2)))
                )
            else:
                season_data = ds.sel(time=(ds.time.dt.year == year) & condition, method="nearest")
            result[s].append(season_data.heatwave.sum().item())

    # Create the new dataset season
    season_ds = xr.Dataset({
        "DJF": (("year",), result["1"]),
        "MAM": (("year",), result["2"]),
        "JJA": (("year",), result["3"]),
        "SON": (("year",), result["4"]),
    }, coords={"year": result["year"]})

    season_ds.to_dataframe().reset_index().to_csv("season_heatwave.csv", index=False)

def main(tmax, percent):
    #tmax is the temperature
    tmax = xr.open_dataset(tmax)
    tmax = tmax.sel(time = tmax.time[tmax.time.dt.year > 1990])
    time = pd.to_datetime(tmax.time.values)
    percent = xr.open_dataset(percent)

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #1 if is the start of heatwave date and end day, 0 else
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("The nexts years are being consideraded:")
    print(years)
    hw = np.zeros(years.size) #Will save the heatwave
    season = np.zeros((4, years.size))
    hw_cont = np.zeros(years.size)

    df = heatwave_Dataset(tmax, percent) 
    Season_heatwave(df)
    df.to_dataframe().reset_index().to_csv("heatwave_ref.csv", index=False)

if __name__ == "__main__":
    param1 = sys.argv[1]
    param2 = sys.argv[2]

    main(param1, param2)
