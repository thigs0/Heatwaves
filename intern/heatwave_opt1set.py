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
from support import heatwave
warnings.filterwarnings("ignore")

def main(tmax, percentmax):
    tmax = xr.open_dataset(tmax)
    percentmax = xr.open_dataset(percentmax)
    years = np.arange( tmax.time.dt.year[0].to_numpy().item(), tmax.time.dt.year[-1].to_numpy().item() + 1 )
    print("The Heatwaves are of these years:")
    print(years)

    ds = heatwave(dataset_tmax=tmax, percent_tmax=percentmax, opt=1, n=3) 
    ds.to_netcdf('heatwave_opt1set.nc')
    del ds

if __name__ == "__main__":
    param1 = sys.argv[1] #tmax netcdf
    param2 = sys.argv[2] #percentmax

    main(param1, param2)
