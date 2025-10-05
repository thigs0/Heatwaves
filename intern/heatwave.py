"""
calculate the heatwaves per year and your sizes
Save in a output .csv
"""
from alive_progress import alive_bar
import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def heatwave_Dataset(tmax:xr.Dataset, percentmax:xr.Dataset) -> xr.Dataset: #return a dataframe with temperature and reference
    tmax = tmax.where(tmax.time.dt.year > 1990, drop=True)

    tmax = tmax['tmax'] if isinstance(tmax, xr.Dataset) else tmax
    percentmax = percentmax['tmax'] if isinstance(percentmax, xr.Dataset) else percentmax

    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    #rename coords of tmax, tmin, percentmax and percentmin 
    if "latitude" in tmax.coords:
        ds = tmax.rename({"latitude": "lat"})
    if "longitude" in tmax.coords:
        ds = tmax.rename({"longitude": "lon"})
    if "latitude" in percentmax.coords:
        ds = percentmax.rename({"latitude": "lat"})
    if "longitude" in percentmax.coords:
        ds = percentmax.rename({"longitude": "lon"})

    # Add dayofyear at dataframe and percentmax
    percentmax = percentmax.assign_coords(dayofyear=percentmax.time.dt.dayofyear)
    percent_daily = percentmax.groupby('dayofyear').mean(dim='time')
    percent_daily = percent_daily.assign_coords(dayofyear=percent_daily['dayofyear'])
    data_dayofyear = tmax.time.dt.dayofyear
    percentmax_expanded = percent_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmax_expanded = percentmax_expanded.assign_coords(time=tmax.time)
    percentmax = percentmax_expanded

    percentmax = percentmax.broadcast_like(tmax)

    #Calcule heatwave
    year = years[0]
    print("Calculating the heatwaves")
    greater = (tmax > percentmax).astype(int)
    rolling_sum = greater.rolling(time=3).sum()
    heatwave_flag = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)
    heatwave_raw = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)

    #Create a mask to register only the first day and jump others
    heatwave_events = heatwave_raw.copy(deep=True)
    heatwave_events[:] = 0

    i = 0
    while i < len(heatwave_raw.time):
        if heatwave_raw.isel(time=i):
            heatwave_events[i] = 1  # Mark of event start
            i += 3  #jump next two days (three days per event)
        else:
            i += 1

    ref_max = percentmax.broadcast_like(tmax)
    #out netcdf
    out_ds = xr.Dataset({
        'tmax': tmax,
        'refmax': ref_max,
        'greater': greater,
        'heatwave': heatwave_events,
    })
    out_ds.to_dataframe().reset_index().to_csv("heatwave_ref.csv", index=False)
    return out_ds

def Season_heatwave(ds: xr.Dataset) -> xr.Dataset:
    """
    Need a Dataset with variable 'heatwave' binary and return a new dataset with the sum per season."""

    years = np.arange(ds.time.dt.year.min().item(), ds.time.dt.year.max().item() + 1)
    seasons = {
        '1': ((ds.time.dt.month == 12) | (ds.time.dt.month <= 2)),
        '2': ((ds.time.dt.month >= 3) & (ds.time.dt.month <= 5)),
        '3': ((ds.time.dt.month >= 6) & (ds.time.dt.month <= 8)),
        '4': ((ds.time.dt.month >= 9) & (ds.time.dt.month <= 11)),
    }

    # Create the array of results
    result = {season: [] for season in seasons}
    result["year"] = []

    for year in years:
        result["year"].append(year)
        for s, condition in seasons.items():
            if s == '1':
                # dezember of last year + Jan+Feb od current year
                season_data = ds.sel(
                    time=(((ds.time.dt.year == year - 1) & (ds.time.dt.month == 12)) |
                          ((ds.time.dt.year == year) & (ds.time.dt.month <= 2)))
                )
            else:
                season_data = ds.sel(time=(ds.time.dt.year == year) & condition, method="nearest")
            result[s].append(season_data.sum().item())

    # Create a season dataset
    season_ds = xr.Dataset({
        "DJF": (("year",), result["1"]),
        "MAM": (("year",), result["2"]),
        "JJA": (("year",), result["3"]),
        "SON": (("year",), result["4"]),
    }, coords={"year": result["year"]})

    season_ds.to_dataframe().reset_index().to_csv("season_heatwave.csv", index=False)

def main(tmax:xr.Dataset, percentmax:xr.Dataset):
    #tmax é o nc de teperatura que iremos avaliar
    tmax = xr.open_dataset(tmax)

    percentmax = xr.open_dataset('percentmax.nc')
    time = pd.to_datetime(tmax.time.values)

    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("The Heatwaves are of these years:")
    print(years)

    ds = heatwave_Dataset(tmax, percentmax) 
    Season_heatwave(ds.heatwave)

if __name__ == "__main__":
    param1 = sys.argv[1] #tmax netcdf
    param2 = sys.argv[2] #percentmax

    main(param1, param2)
