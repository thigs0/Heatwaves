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
            normal_val = ds_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                        (ds_norm.time.dt.day == day))).isel(time=0)

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
                    if sum(value.values) == n: #start a heatwave, keep goin 
                        k = n #days after three heat days
                        while i + k + 1 < len_date and ds.sel(time=ds.time.values[i + k + 1], lat=lat, lon=lon):
                            k+=1
                        heat[i] = k #number of days with heatwave
                        i+=k
                        bar(k) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                out.loc[dict(lat=lat, lon=lon)] = heat 

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

    #Calcule heatwave
    print('Calculating hotdays')
    greater = hotdays(tmax, percentmax)
    print("Calculating the heatwaves")
    heatwave_events = heatwave(greater, 3)

    refmax = percentmax
    #out netcdf
    out_ds = xr.Dataset({
        'tmax': tmax,
        'refmax': refmax,
        'greater': greater,
        'heatwave': heatwave_events,
    })
    out_ds.to_netcdf('heatwave_opt4set.nc')
    return out_ds

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

if __name__ == "__main__":
    param1 = sys.argv[1] #tmax netcdf
    param2 = sys.argv[2] #percentmax

    main(param1, param2)
