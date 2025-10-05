"""
Calculate the heatwaves per year and your sizes.
SAve the output file in a .csv
"""

import xarray as xr
import numpy as np
import datetime
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")

def Season_heatwave(df:pd.DataFrame)->None:
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

def main(tmax, tmin):
    #tmax is the netcdf temperature that we use
    tmax = xr.open_dataset(tmax)
    tmin = xr.open_dataset(tmin)
    time = pd.to_datetime(tmax.time.values)
    percentmax = xr.open_dataset("percent.nc") #need percent of min e max
    percentmin = xr.open_dataset("percent.nc") #need percent of min e max

    i = 0
    n = len(tmax.time.values)
    r = np.zeros(n) #! if this day start a heatwave, 0 else
    years = np.arange( time.year[0], time.year[n-1]+1 )
    hw = np.zeros(years.size) #Will save the heatwave
    season = np.zeros((4, years.size))
    hw_cont = np.zeros(years.size)

    #Calculate the heatwave
    year = years[0]
    while i < n-3: #While we are not at end
        tpercent = 0
        if (time[i] + pd.DateOffset(day=3)).year != year: #Register the heatwave at same year, without jump to next
            i+=3
            year+=1
        else:
            for k in range(3): 
                x = time[i] + pd.DateOffset(day=k)
                ymax = percent.tmax.values[ ((percent.time.dt.month == x.month) & (percent.time.dt.day == x.day)) ].flatten() #value of percentile at day
                ymin = percent.tmin.values[ ((percent.time.dt.month == x.month) & (percent.time.dt.day == x.day)) ].flatten() #value of percentile at day
                tpercent += ((ymax < tmax.tmax.values[i+k]) & (ymin < tmin.tmin.values[i+k] )) #compare the percentile with each 3 days of max temperature and min
            if tpercent == 3: #If all three days above the percentile
                r[i] = 1
                i+=3
            else:
                i+=1
        
    #calcule the heatwaves per year
    for j,y in enumerate(years):
        hw[j] = np.sum( r[time.year == y] ) #sum all heatwaves at each year y
    #To each year, calculate the quantiti of heatwaves
    for k, y in enumerate(years):
        datemax = tmax.tmax.values[ time.year == y ] #all dates of year y
        datemin = tmin.tmin.values[ time.year == y ] #all dates of year y
        i=0
        while i < date.size: #follow all days of year y
            c=0
            while i < date.size and datemax[i] > percent.tmax.values[i] and datemin[i] > percent.tmin.values[i]: # Enquanto o arquivo tem dados e temos uma onda de calor
                c+=1 #if is a day that start a heatwave
                i+=1 #jump one day
            if c > hw_cont[k]: # if a heatwave is bigger that last year
                hw_cont[k] = c
            i += 1

    #To a continuos season
    for k, y in enumerate(years):
        if k != 0 :
            datemin = tmin.tmin.values[ (
                (time.year == y-1) & (time.month == 12) |
                (time.year == y) & (time.month ==1) |
                (time.year == y) & (time.month ==2)
            ) ].flatten() #all dates of year y
            datemax = tmax.tmax.values[ (
                (time.year == y-1) & (time.month == 12) |
                (time.year == y) & (time.month ==1) |
                (time.year == y) & (time.month ==2)
            ) ].flatten() #all dates of year y
            i=0

            while i < date.size: #follow all days of year y
                c=0
                while i < date.size and datemax[i] > percent.tmax.values[i] and datemin[i] > percent.tmin.values[i]: # while the file has data and we have a heatwave
                    c+=1 #is a day with heatwave
                    i+=1 #jump one day
                if c > season[0][k]: # if the current heatwave is bigger than last, to same year
                    season[0][k] = c
                i += 1


        for zi, z in enumerate((3,6,9)):
            datemax = tmax.tmax.values[ (
                (time.year == y-1) & (time.month ==z) |
                (time.year == y) & (time.month ==z+1) |
                (time.year == y) & (time.month == z+2)
            ) ].flatten() #all dates of year y
            datemin = tmin.tmin.values[ (
                (time.year == y-1) & (time.month == 12) |
                (time.year == y) & (time.month ==1) |
                (time.year == y) & (time.month ==2)
            ) ].flatten() #all dates of year y
            i=0

            while i < date.size: #follow all dates of year y
                c=0
                while i < date.size and datemax[i] > percent.tmax.values[i] and datemin[i] > percent.tmin.values: # while the file has data and we have a heatwave
                    c+=1 #is a date that begin a heatwave
                    i+=1 #jump one day
                if c > season[zi+1][k]: # if the current heatwave is bigger than last, to same year
                    season[zi+1][k] = c
                i += 1


    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["HeatWave"] = hw[years > 1990]
    df.to_csv("Heatwave.csv")

    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["Heatwave_days"] = hw_cont[years > 1990]
    df.to_csv("Heatwaves_days.csv")
    
    df = pd.DataFrame()
    df["time"] = time[time.year > 1990]
    df["cdh"] = r[time.year > 1990]
    df.to_csv("Heatwaves_complete.csv")

    df = pd.DataFrame()
    df["time"] = years[years > 1990]
    df["1"] = season[0][years > 1990]
    df["2"] = season[1][years > 1990]
    df["3"] = season[2][years > 1990]
    df["4"] = season[3][years > 1990]
    df.to_csv("season.csv")
    
    df = pd.read_csv("Heatwaves_complete.csv")
    df["time"] = pd.to_datetime(df["time"])
    df = df[ df["time"].dt.year >= 1991 ]
    Season_heatwave(df)

if __name__ == "__main__":
    parametro1 = sys.argv[1]
    parametro2 = sys.argv[2]

    main(parametro1, parametro2)
