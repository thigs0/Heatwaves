import pandas as pd
import sys
import xarray as xr

def main(p1):
    """This function make the txt file chenge to netcdf"""
    #p1 é o arquivo txt que queremos converter para netcdf
    df = pd.read_csv(p1)
    #df.columns need be [time, tmin, lat, lon]
    names = ["time", "tmin", "tmax", "pr", "lat", "lon"]
    if len(df.columns) != 4 or len(set(df.columns).intersection(names)) != 4:
        print(set(df.columns).intersection(names))
        raise "The text file need have four columns time, tmin/tmax/pr , lat, lon"
    else:
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index(["time", "lat","lon"])
        ds = df.to_xarray()
        ds = xr.Dataset(ds)
        print(f"{p1[:-4]}.nc")
        ds.to_netcdf(f"{p1[:-4]}.nc")


if __name__ == "__main__":
    parametro = sys.argv[1]
    main(parametro)
