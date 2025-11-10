from alive_progress import alive_bar
import xarray as xr
import numpy as np
import pandas as pd
import warnings

def heatwave(dataset_tmax:xr.Dataset, opt:int, n:int, dataset_tmin=xr.Dataset(), percent_tmax=xr.Dataset(), percent_tmin=xr.Dataset(),
             with_anomaly=False, with_season=False) -> xr.Dataset:
    match opt:
        case 1:
            greater = hotdays_opt1(dataset_tmax, percent_tmax)
            if with_anomaly:
                return xr.Dataset()
            else:
                return heatwave_opt1(greater, n)
        
        case 2:
            greater = hotdays_opt2(dataset_tmax, percent_tmax, dataset_tmin, percent_tmin) 
            if with_anomaly:
                return heatwave_opt2_with_anomaly(greater, dataset_tmax, percent_tmax, n)
            else:
                return heatwave_opt2(greater, n)

        case 3:
            return xr.Dataset()
        
        case 4:
            greater = hotdays_opt1(dataset_tmax, percent_tmax)
            if with_anomaly:
                return xr.Dataset()
            else:
                return heatwave_opt4(greater)
        
        case _:
            raise ValueError("Invalid value")
        
def hotdays_opt2(ds, ds_norm, ds2, ds2_norm) -> xr.Dataset:
    out = ds.copy()
    print(ds)
    
    # Initialize heatwave variable with False values
    out['greater'] = xr.zeros_like(ds.tmax, dtype=bool)

    # Percorre cada data do dataset original
    with alive_bar(len(ds.time)) as bar:
        for i, date in enumerate(ds.time):
            # export the date value
            this_date = date.values
            month = date.dt.month.item()
            day = date.dt.day.item()

            # current date
            ds1_current = ds.sel(time=this_date)
            ds2_current = ds2.sel(time=this_date)

            # Valor normal para aquele dia/mês
            ds1_nor = ds_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                        (ds_norm.time.dt.day == day))).isel(time=0)
            ds2_nor = ds2_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                        (ds_norm.time.dt.day == day))).isel(time=0)

            # Calculate heatwave condition - FIXED LINE
            heatwave_condition = ((ds1_current.tmax > ds1_nor.tmax) & 
                                 (ds2_current.tmin > ds2_nor.tmin))
            
            # Assign only to the heatwave variable - FIXED LINE
            out['greater'].loc[dict(time=this_date)] = heatwave_condition
            
            bar() # Update the progress bar
    return out

def hotdays_opt1(ds, ds_norm):
    out = ds.copy()
    print(ds)
    out['greater'] = xr.zeros_like(ds.tmax, dtype=bool)

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

            out['greater'].loc[dict(time=this_date)] = (current_val["tmax"] > normal_val["tmax"]).astype(int)
            bar() # Update the progress bar
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

def heatwave_opt4(ds:xr.Dataset):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = ds.copy()

    # Initialize temporal variables as boolean arrays  
    out['heatwave'] = xr.zeros_like(ds.greater, dtype=bool)
    out['extention'] = xr.zeros_like(ds.greater, dtype=bool)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-3+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+3)
                extention = np.zeros(len_date+3)
                i = 0
                while i < len_date:
                    value = ds.greater.sel(time=ds.time.values[i:i + 3 + 1], lat=lat, lon=lon)
                    if sum(value.values) == 3: # begin a heatwave
                        k=i+3+1
                        while k < len_date and ds.greater.sel(time=ds.time.values[k], lat=lat, lon=lon) == 1:
                            k+=1
                        heat[i] = 1
                        extention[i] = k
                        i=k-1
                        bar(k-1) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                out.heatwave.loc[dict(lat=lat, lon=lon)] = heat
                out.extention.loc[dict(lat=lat, lon=lon)] = extention 
    return out

def heatwave_opt1(ds:xr.Dataset, n:int):
    ds = ds.astype(int)
    out = ds.copy()

    # Initialize temporal variables as boolean arrays  
    out['heatwave'] = xr.zeros_like(ds.greater, dtype=bool)

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
    out['anomaly_tmax'] = xr.zeros_like(ds.greater, dtype=bool)
    out['anomaly_tmin'] = xr.zeros_like(ds.greater, dtype=bool)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                anom_tmax = np.zeros(len_date+n)
                anom_tmin = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = ds.greater.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n:
                        heat[i] = 1
                        anom_tmax[i] = temperature.tmax.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon).sum() - percent.tmax.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon).sum()
                        anom_tmax[i] = temperature.tmax.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon).sum() - percent.tmax.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon).sum()
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                out.heatwave.loc[dict(lat=lat, lon=lon)] = heat
                out.anomaly.loc[dict(lat=lat, lon=lon)] = heat 
    return out