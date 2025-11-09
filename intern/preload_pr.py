import xarray as xr
import sys
import gc

def main(pr): 
    print("Preloading pr file")
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
    del pr
    gc.collect()

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    main(parametro1)
