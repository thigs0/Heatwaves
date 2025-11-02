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
from support import heatwave
warnings.filterwarnings("ignore")

def main(tmax, tmin, percentmax, percentmin):
    #tmax is the netcdf temperature that we use
    tmax = xr.open_dataset(tmax)
    tmin = xr.open_dataset(tmin)
    percentmax = xr.open_dataset(percentmax) #need percent of min e max
    percentmin = xr.open_dataset(percentmin) #need percent of min e max

    ds = heatwave(dataset_tmax= tmax, dataset_tmin=tmin, percent_tmax=percentmax, percent_tmin=percentmin,
                  opt=2, n=3)
    ds.to_netcdf('heatwave_opt2set.nc')
    del ds

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    parametro2 = sys.argv[2]
    parametro3 = sys.argv[3]
    parametro4 = sys.argv[4]

    main(parametro1, parametro2, parametro3, parametro4)
