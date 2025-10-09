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
warnings.filterwarnings("ignore")

def hotdays(ds, ds_norm, ds2, ds2_norm) -> xr.Dataset:
    timer=len(ds.time.values)
    out = xr.zeros_like(ds, dtype=bool)

    # Percorre cada data do dataset original
    with alive_bar(len(ds.time)) as bar:
        for i, date in enumerate(ds.time):
            # export the date value
            this_date = date.values
            month = date.dt.month.item()
            day = date.dt.day.item()

            # current date
            ds1_current = ds.sel(time=this_date)
            ds2_current = ds2.sel(time=this_date)

            # Valor normal para aquele dia/mês
            ds1_nor = ds_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                        (ds_norm.time.dt.day == day))).isel(time=0)
            ds2_nor = ds2_norm.sel(time=((ds_norm.time.dt.month == month) & 
                                        (ds_norm.time.dt.day == day))).isel(time=0)

            # Marca como True se for mais quente que o normal
            out.loc[dict(time=this_date)] = ((ds1_current > ds1_nor)&(ds2_current > ds2_nor)).astype(int)
            bar() # Update the progress bar

    return out

def heatwave(ds, n:int):
    # Cria uma cópia booleana com False por padrão
    ds = ds.astype(int)
    out = xr.zeros_like(ds, dtype=int)

    # Percorre cada data do dataset original
    len_date = len(ds.time[:-n+1])-1
    with alive_bar(len_date * len(ds.lat.values) * len(ds.lon.values)) as bar:
        for lat in ds.lat.values:
            for lon in ds.lon.values:
                heat = np.zeros(len_date+n)
                i = 0
                while i < len_date:
                    value = ds.sel(time=ds.time.values[i:i + n + 1], lat=lat, lon=lon)
                    if sum(value.values) == n:
                        heat[i] = 1
                        i+=3
                        bar(3) # Update the progress bar
                    else:
                        i+=1
                        bar() # Update the progress bar
                #out.sel(lat=lat, lon=lon)
                # Marca como True se for mais quente que o normal
                out.loc[dict(lat=lat, lon=lon)] = heat 

    return out


def Season_heatwave(df:xr.Dataset) -> None:
    """
        Recive a dataframe with one if the day had heatwave event and zero else. 
        Than we create a dataframe with heatwaves per season"""
    hw = pd.DataFrame(columns=["time","1","2","3","4"]) #dataframe with results
    hw["time"] = np.arange(df["time"][0].year, df["time"][len(df)-1].year+1) # each year
    
    for i,j in enumerate(hw["time"][:]):
        #dez jan feb
        t = df[((df["time"].dt.year == j-1)&(df["time"].dt.month==12)|(df["time"].dt.year==j)&(df["time"].dt.month <= 2))] #data avaliada
        hw["1"][i] = np.sum(t["cdh"])

        #mar apr may
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=3)&(df["time"].dt.month <= 5)) ]
        hw["2"][i] = np.sum(t["cdh"])

        #jun jul ago
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=6)&(df["time"].dt.month <= 8)) ]
        hw["3"][i] = np.sum(t["cdh"])

        #sep out nov
        t = df[ ((df["time"].dt.year == j)&(df["time"].dt.month >=9)&(df["time"].dt.month <= 11)) ]
        hw["4"][i] = np.sum(t["cdh"])
    hw.to_csv("season_heatwave.csv")

def main(tmax, tmin, percentmax, percentmin):
    #tmax is the netcdf temperature that we use
    tmax = xr.open_dataset(tmax)
    tmin = xr.open_dataset(tmin)
    percentmax = xr.open_dataset(percentmax) #need percent of min e max
    percentmin = xr.open_dataset(percentmin) #need percent of min e max

    #convert types
    try:
        tmax = tmax.rename({'valid_time': 'time'})
    except:
        pass
    try:
        tmin = tmin.rename({'valid_time': 'time'})
    except:
        pass
    try:
        percentmax = percentmax.rename({'valid_time': 'time'})
    except:
        pass
    try:
        percentmin = percentmin.rename({'valid_time': 'time'})
    except:
        pass

    print("Calculating hotdays")
    ds = hotdays(tmax, percentmax, tmin, percentmin) 
    print("Calculating heatwaves")
    Season_heatwave(ds.heatwave)
    ds.to_netcdf('heatwave_opt2set.nc')

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    parametro2 = sys.argv[2]
    parametro3 = sys.argv[3]
    parametro4 = sys.argv[4]

    main(parametro1, parametro2, parametro3, parametro4)
