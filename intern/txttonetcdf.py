import pandas as pd
import sys
import xarray as xr

def main():
    """This function make the txt file chenge to netcdf"""
    #p1 is the file in txt that we want to convert to netcdf
    df = pd.read_csv("../dados/input.csv")
    #df.columns need be [Tmin, Tmax, Pr, Date, Lat, Lon]
    columns =  ['Tmin', 'Tmax', 'Pr', 'Date', 'Lat', 'Lon']
    df = df[columns]
    df.columns = [i.lower() for i in columns]
    df["time"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

    df = df.drop_duplicates()
    df = df.drop(columns=["date"])
    df = df.set_index(["time", "lat","lon"])
    for j in df.columns:
        out = df.drop(columns=df.columns[ df.columns != j ])
        ds = out.to_xarray()
        ds = xr.Dataset(ds)
        ds.to_netcdf(f"../netcdf/{j}.nc")
        print(f"Saved in ../netcdf/{j}.nc")


if __name__ == "__main__":
    main()
