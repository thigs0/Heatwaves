from alive_progress import alive_bar
import xarray as xr
import numpy as np
import pandas as pd
import warnings

def heatwave(dataset_tmax:xr.Dataset, dataset_tmin:xr.Dataset, percent_tmax:xr.Dataset, percent_tmin:xr.Dataset
             ,opt:int, n:int, with_anomaly=False, with_season=False) -> xr.Dataset:
    match opt:
        case 1:
            greater = hotdays(dataset_tmax, percent_tmax, dataset_tmin, percent_tmin)
            if with_anomaly:
                return xr.Dataset()
            else:
                return xr.Dataset()
        
        case 2:
            greater = hotdays(dataset_tmax, percent_tmax, dataset_tmin, percent_tmin) 
            if with_anomaly:
                return heatwave_opt2(greater, n)
            else:
                return heatwave_opt2_with_anomaly(greater, dataset_tmax, percent_tmax, n)

        case 3:
            return xr.Dataset()
        
        case 4:
            greater = hotdays(dataset_tmax, percent_tmax, dataset_tmin, percent_tmin)
            if with_anomaly:
                return xr.Dataset()
            else:
                return xr.Dataset()
        
        case _:
            raise ValueError("Invalid value")
        
def hotdays(ds:xr.Dataset, ds_norm:xr.Dataset, ds2:xr.Dataset, ds2_norm:xr.Dataset) -> xr.Dataset:
    # Create a copy but only modify variables with time dimension
    out = ds.copy()
    
    # Identify which variables have time dimension
    temporal_vars = [var for var in ds.data_vars if 'time' in ds[var].dims]
    
    # Initialize temporal variables as boolean arrays
    
    out['greater'] = xr.zeros_like(ds[temporal_vars[0]], dtype=bool)

    # Pre-compute day-of-year climatologies
    ds_norm_doy = ds_norm.groupby(ds_norm.time.dt.dayofyear).mean()
    ds2_norm_doy = ds2_norm.groupby(ds2_norm.time.dt.dayofyear).mean()

    with alive_bar(len(ds.time)) as bar:
        for i, date in enumerate(ds.time):
            this_date = date.values
            doy = date.dt.dayofyear.item()

            # Current values
            ds1_current = ds.sel(time=this_date)
            ds2_current = ds2.sel(time=this_date)

            # Normal values using day-of-year
            try:
                ds1_nor = ds_norm_doy.sel(dayofyear=doy)
            except KeyError:
                ds1_nor = ds_norm.mean(dim='time')
            
            try:
                ds2_nor = ds2_norm_doy.sel(dayofyear=doy)
            except KeyError:
                ds2_nor = ds2_norm.mean(dim='time')

            # Calculate condition
            condition = (ds1_current > ds1_nor) & (ds2_current > ds2_nor)
            
            # Update only temporal variables
            for var in temporal_vars:
                if var in condition.data_vars:
                    out['greater'].loc[dict(time=this_date)] = condition[var]
            
            bar()

    return out

def heatwave_opt2(ds:xr.Dataset, n:int):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = ds.copy()

    # Initialize temporal variables as boolean arrays  
    out['heatwave'] = xr.zeros_like(ds.greater, dtype=bool)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = ds.greater.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n:
                        heat[i] = 1
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                out.heatwave.loc[dict(lat=lat, lon=lon)] = heat 
    return out

def heatwave_opt2_with_anomaly(ds:xr.Dataset, temperature:xr.Dataset, percent:xr.Dataset, n:int):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = ds.copy()

    # Initialize temporal variables as boolean arrays  
    out['heatwave'] = xr.zeros_like(ds.greater, dtype=bool)
    out['anomaly'] = xr.zeros_like(ds.greater, dtype=bool)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                anoma = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = ds.greater.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n:
                        heat[i] = 1
                        anoma[i] = sum(percent.tmax.sel(time=hotdays.time.values[i:i + n + 1], lat=lat, lon=lon).values) - sum(temperature.tmax.sel(time=hotdays.time.values[i:i + n + 1], lat=lat, lon=lon).values)
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                out.heatwave.loc[dict(lat=lat, lon=lon)] = heat 
    return out
