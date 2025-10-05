"""
    This code calculate the SPI of netcdf4 file with precipitation
"""

import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import xclim
import warnings
warnings.filterwarnings("ignore")

def main(pr):
    #pr is the complete netcdf4 of precipitation
    ds = xr.open_dataset(pr) #multi-year mean of reference
    ds_cal = ds.sel(time = ds.time[ ds.time.dt.year<1991 ])
    ds = ds.sortby("time")
    ds_cal = ds_cal.sortby("time")
    ds.pr.attrs['units'] = 'mm/day'
    ds_cal.pr.attrs['units'] = 'mm/day'
    n = len(ds_cal.time.values)
    ds = xclim.indices.standardized_precipitation_index(ds['pr'], pr_cal=ds_cal["pr"],
            cal_start= f"{ds_cal.time[0].dt.year}-01-01", 
            cal_end=f"{ds_cal.time[n-1].dt.year}-12-31", freq='MS')
    # add the result to our set of original data
    ds.to_netcdf("spi.nc")

if __name__ == "__main__":
    parametro1 = sys.argv[1]

    # call the function with paramns gived
    main(parametro1)
