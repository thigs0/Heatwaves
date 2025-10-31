"""
calculate the heatwaves per year and your sizes
Save in a output .csv
"""
from alive_progress import alive_bar
import xarray as xr
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def hotdays(ds, ds_norm):
    timer=len(ds.time.values)
    out = xr.zeros_like(ds, dtype=bool)

    # Percorre cada data do dataset original
    with alive_bar(len(ds.time)) as bar:
        for i, date in enumerate(ds.time):
            # Extrai o valor da data
            this_date = date.values
            month = date.dt.month.item()
            day = date.dt.day.item()

            # Valor do dia atual
            current_val = ds.sel(time=this_date)

            # Valor normal para aquele dia/mês
            try:
                normal_val = ds_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                            (ds_norm.time.dt.day == day))).isel(time=0)
            except:
                normal_val = xr.zeros_like(ds_norm, dtype=bool)*6000
                print(f'Error with date {day}/{month}')
            print(current_val)
            # Marca como True se for mais quente que o normal
            out.loc[dict(time=this_date)] = (current_val > normal_val).astype(int)
            bar() # Update the progress bar

    return out

def heatwave(ds, n:int):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = xr.zeros_like(ds, dtype=int)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = ds.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n:
                        heat[i] = 1
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                #out.sel(lat=lat, lon=lon)
                # Marca como True se for mais quente que o normal
                out.loc[dict(lat=lat, lon=lon)] = heat 

    return out

def anomaly(hotdays, reference, percent, n:int):
    # Cria uma cópia booleana com False por padrão
    hotdays = hotdays.astype(int)
    out = xr.zeros_like(hotdays, dtype=int)

    # Percorre cada data do dataset original
    len_date = len(hotdays.time[:-n+1])-1
    with alive_bar(len_date * len(hotdays.lat.values) * len(hotdays.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                anoma = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = hotdays.sel(time=hotdays.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n: #is a heatwave
                        anoma[i] = sum(percent.tmax.sel(time=hotdays.time.values[i:i + n + 1], lat=lat, lon=lon).values) - sum(reference.sel(time=hotdays.time.values[i:i + n + 1], lat=lat, lon=lon).values)
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        anoma[i] = 0
                        bar() # Update the progress bar
                #out.sel(lat=lat, lon=lon)
                # Marca como True se for mais quente que o normal
                out.loc[dict(lat=lat, lon=lon)] = anoma
    return out

def heatwave_Dataset(tmax, percentmax) -> xr.Dataset: #return a dataframe with temperature and reference
    tmax = tmax.where(tmax.time.dt.year > 1990, drop=True)

    tmax = tmax['tmax'].fillna(0) if isinstance(tmax, xr.Dataset) else tmax.fillna(0)
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

    """
    # Add dayofyear at dataframe and percentmax
    percentmax = percentmax.assign_coords(dayofyear=percentmax.time.dt.dayofyear)
    percent_daily = percentmax.groupby('dayofyear').mean(dim='time')
    percent_daily = percent_daily.assign_coords(dayofyear=percent_daily['dayofyear'])
    data_dayofyear = tmax.time.dt.dayofyear
    percentmax_expanded = percent_daily.sel(dayofyear=data_dayofyear, method='nearest')
    percentmax_expanded = percentmax_expanded.assign_coords(time=tmax.time)
    percentmax = percentmax_expanded

    percentmax = percentmax.broadcast_like(tmax)
    percentmax = percentmax.sel(lat=tmax.lat.values, lon=tmax.lon.values).fillna(0) #If some coordenates wrongs come, ignore
    percentmax = percentmax.drop_vars('dayofyear')
    """

    #Calcule heatwave
    print('Calculating hotdays')
    greater = hotdays(tmax, percentmax)
    print("Calculating the heatwaves")
    heatwave_events = heatwave(greater, 3)
    print("Calculating the heatwave anomaly")
    anomaly_value = anomaly(greater, tmax, percentmax, 3)
    """
    rolling_sum = greater.rolling(time=3).sum()
    heatwave_raw = (rolling_sum >= 3).shift(time=-2).fillna(0).astype(int)

    #Create a mask to register only the first day and jump others
    heatwave_events = heatwave_raw.copy(deep=True)
    heatwave_events[:] = 0

    i = 0
    while i < len(heatwave_raw.time):
        if heatwave_raw.isel(time=i).any():
            heatwave_events[i] = 1  # Mark of event start
            i += 3  #jump next two days (three days per event)
        else:
            i += 1
    """

    refmax = percentmax.broadcast_like(tmax)
    #out netcdf
    out_ds = xr.Dataset({
        'tmax': tmax,
        'refmax': refmax,
        'greater': greater,
        'anomaly': anomaly_value,
        'heatwave': heatwave_events,
    })
    out_ds.to_netcdf('heatwave_opt1set.nc')
    return out_ds

def Season_heatwave(ds: xr.Dataset):
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

def main(tmax, percentmax):
    tmax = xr.open_dataset(tmax)

    try: #Some files come with valid_time name
        tmax = tmax.rename({'valid_time': 'time'})
    except:
        pass
    percentmax = xr.open_dataset(percentmax)
    try: #Some files come with valid_time name
        percentmax = percentmax.rename({'valid_time': 'time'})
    except:
        pass
 
    time = pd.to_datetime(tmax.time.values)

    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item()+1 )
    print("The Heatwaves are of these years:")
    print(years)

    ds = heatwave_Dataset(tmax, percentmax) 
    Season_heatwave(ds.heatwave)
    ds.to_netcdf('heatwave_opt1set.nc')

if __name__ == "__main__":
    param1 = sys.argv[1] #tmax netcdf
    param2 = sys.argv[2] #percentmax

    main(param1, param2)
