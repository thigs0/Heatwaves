import pandas as pd
import sys
import xarray as xr

def main():
    """This function make the txt file change to netcdf"""
   #p1 é o arquivo txt que queremos converter para netcdf
    df = pd.read_csv("../dados/input.csv")
    #df.columns need be [Tmin, Tmax, Pr, Date, Lat, Lon]
    columns =  ['Tmin', 'Tmax', 'Pr', 'Date', 'Lat', 'Lon']
    df = df[columns]
    df.columns = [i.lower() for i in columns]
    k=0

    try:
        df["time"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    except:
        k+=1

    try:
        df["time"] = pd.to_datetime(df["date"], format="%m-%d-%y")
    except:
        k+=1

    try:
        df["time"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    except:
        k+=1


    if k==3:
        raise "Error datatime error format"

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
