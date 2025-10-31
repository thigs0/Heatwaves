"""
Calculate the heatwaves per year and your sizes.
SAve the output file in a .csv
"""
from alive_progress import alive_bar
import xarray as xr
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def hotdays(ds, ds_norm, ds2, ds2_norm) -> xr.Dataset:
    # Create a copy but only modify variables with time dimension
    out = ds.copy()
    
    # Identify which variables have time dimension
    temporal_vars = [var for var in ds.data_vars if 'time' in ds[var].dims]
    
    # Initialize temporal variables as boolean arrays
    for var in temporal_vars:
        out[var] = xr.zeros_like(ds[var], dtype=bool)

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
                    out[var].loc[dict(time=this_date)] = condition[var]
            
            bar()

    return out

def heatwave(ds, n:int):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = ds.copy()
    
    # Identify which variables have time dimension
    temporal_vars = [var for var in ds.data_vars if 'time' in ds[var].dims]
    
    # Initialize temporal variables as boolean arrays
    for var in temporal_vars:
        out[var] = xr.zeros_like(ds[var], dtype=bool)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    try:
                        value = ds.tmax.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    except:
                        value = ds.tmin.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    
                    if sum(value.values) == n:
                        heat[i] = 1
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                #out.sel(lat=lat, lon=lon)
                # Marca como True se for mais quente que o normal
                print(out)
                try:
                    out.tmax.loc[dict(lat=lat, lon=lon)] = heat 
                except:
                    out.tmin.loc[dict(lat=lat, lon=lon)] = heat 

    return out

def main(tmax, tmin, percentmax, percentmin):
    #tmax is the netcdf temperature that we use
    tmax = xr.open_dataset(tmax)
    tmin = xr.open_dataset(tmin)
    percentmax = xr.open_dataset(percentmax) #need percent of min e max
    percentmin = xr.open_dataset(percentmin) #need percent of min e max

    #convert types
    try:
        tmax = tmax.rename({'valid_time': 'time'})
    except:
        pass
    try:
        tmin = tmin.rename({'valid_time': 'time'})
    except:
        pass
    try:
        percentmax = percentmax.rename({'valid_time': 'time'})
    except:
        pass
    try:
        percentmin = percentmin.rename({'valid_time': 'time'})
    except:
        pass

    print("Calculating hotdays")
    greater = hotdays(tmax, percentmax, tmin, percentmin) 
    print("Calculating heatwaves")
    ds = heatwave(greater, 3)
    ds.to_netcdf('heatwave_opt2set.nc')

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    parametro2 = sys.argv[2]
    parametro3 = sys.argv[3]
    parametro4 = sys.argv[4]

    main(parametro1, parametro2, parametro3, parametro4)
