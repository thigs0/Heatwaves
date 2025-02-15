"""
    Este código calcula o SPI do arquivo netcdf4 com a precipitação 
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
    #pr é o netcdf de precipitação completo

    ds = xr.open_dataset(pr) #média multi-year da referência
    ds_cal = ds.sel(time = ds.time[ ds.time.dt.year<1991 ])
    ds = ds.sortby("time")
    ds_cal = ds_cal.sortby("time")
    ds.pr.attrs['units'] = 'mm/day'
    ds_cal.pr.attrs['units'] = 'mm/day'
    n = len(ds_cal.time.values)
    ds = xclim.indices.standardized_precipitation_index(ds['pr'], pr_cal=ds_cal["pr"],
            cal_start= f"{ds_cal.time[0].dt.year}-01-01", 
            cal_end=f"{ds_cal.time[n-1].dt.year}-12-31", freq='MS')
    # Adicionar o resultado ao conjunto de dados original
    ds.to_netcdf("spi.nc")

if __name__ == "__main__":
    parametro1 = sys.argv[1]

    # Chama a função com os parâmetros fornecidos
    main(parametro1)
