import pandas as pd
import numpy as np
import xarray as xr

ds = xr.open_dataset("../tmax.nc")

tmax_ref = ds.sel(time = ds.time[ ds.time.dt.year <1991 ])
tmax_f = ds.sel( time = ds.time[ ds.time.dt.year>=1991 ] )

tmax_ref.to_netcdf("../tmax_ref.nc")
tmax_f.to_netcdf("../tmax_f.nc")
