"""
Calculate the heatwaves per year and your sizes.
SAve the output file in a .csv
"""
from alive_progress import alive_bar
import xarray as xr
import sys
import warnings
warnings.filterwarnings("ignore")

def main(pr):
    #pr is the netcdf temperature that we use
    print("Preloading tmin file")
    pr = xr.open_dataset(pr)

    #convert types
    try:
        pr = pr.rename({'valid_time': 'time'})
    except:
        pass
    try:
        pr = pr.rename({'tas': 'pr'})
    except:
        pass
    
    pr.pr.to_netcdf('temporary/temporary_pr.nc')

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
