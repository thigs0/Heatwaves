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

def main(tmin):
    #tmin is the netcdf temperature that we use
    print("Preloading tmin file")
    tmin = xr.open_dataset(tmin)

    #convert types
    try:
        tmin = tmin.rename({'valid_time': 'time'})
    except:
        pass
    try:
        tmin = tmin.rename({'tas': 'tmin'})
    except:
        pass
    
    tmin.tmin.to_netcdf('temporary/temporary_tmin.nc')
    del tmin
    gc.collect()

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
