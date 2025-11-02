"""
Calculate the heatwaves per year and your sizes.
SAve the output file in a .csv
"""
from alive_progress import alive_bar
import xarray as xr
import sys
import warnings
import gc
warnings.filterwarnings("ignore")

def main(tmax):
    #tmax is the netcdf temperature that we use
    print("Preloading tmin file")
    tmax = xr.open_dataset(tmax)

    #convert types
    try:
        tmax = tmax.rename({'valid_time': 'time'})
    except:
        pass
    try:
        tmax = tmax.rename({'tas': 'tmax'})
    except:
        pass
    
    tmax.tmax.to_netcdf('temporary/temporary_tmax.nc')
    del tmax
    gc.collect()

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
