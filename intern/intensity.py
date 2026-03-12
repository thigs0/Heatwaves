"""
    This code need a heatwave file pre-defined with percentil max and minimum.
    To ech latitude and longitude, get the index EHF.

"""

from alive_progress import alive_bar
import xarray as xr
from numpy import zeros, maximum
import sys

def main(hw, percentmax, percentmin):
    hw = xr.open_dataset(hw)
    percentmax = xr.open_dataset(percentmax) #need percent of min e max
    percentmin = xr.open_dataset(percentmin) #need percent of min e max
    percent = (percentmax.tmax +percentmin.tmin)/2 #average between maximum and minumum temperature
    # Initialize hw variable with False values
    hw['temp'] = (hw.tmax+hw.tmin)/2
    hw['EHI_sig'] = xr.zeros_like(hw.tmax, dtype=float)
    hw['EHI_accl'] = xr.zeros_like(hw.tmax, dtype=float)
    hw['EHF'] = xr.zeros_like(hw.tmax, dtype=float)
    #local variable with defined size, change position for each loop
    EHI_sig = zeros( len(hw.time) )
    EHI_accl = zeros( len(hw.time) )
    EHI = zeros( len(hw.time) )
    #individual to each point
    with alive_bar(len(hw.time[:-3].values) * len(hw.lat.values) * len(hw.lon.values)) as bar:#Ignore the last three days
        for lat in hw.lat.values:
            for lon in hw.lon.values:
                for i, date in enumerate(hw.time[:-3]):
                    month = date.dt.month.item()
                    day = date.dt.day.item()
                    #significance index (EHF) algorith
                    EHI_sig[i] = hw.temp.sel(
                                time=hw.time[i:i+3],
                                lat=lat, lon=lon).sum().values / 3
                    EHI_sig[i] -= percent.sel(time=((percent.time.dt.month == month) &
                                                    (percent.time.dt.day == day)),
                                                     lat=lat, lon=lon).values.item()
                    #acclimatisation index (EHI) algorith
                    EHI_accl[i] = hw.temp.sel(
                                time=hw.time[i:i+3],
                                lat=lat, lon=lon).sum().values / 3
                    if i < 31:  #Cant look before 31 days when not exist, error, consider 0
                        EHI[i] = 0
                    else:
                        EHI_accl[i] -= hw.temp.sel(
                                time=hw.time[i-31:i-1],
                                lat=lat, lon=lon).sum().values / 30
                    bar()
                #save local arrays at netcdf file
                hw.EHI_sig.loc[dict(lat=lat, lon=lon)] = EHI_sig
                hw.EHI_accl.loc[dict(lat=lat, lon=lon)] = EHI_accl
                #Get product by element and the second consider the max between 1 and each position
                hw.EHF.loc[dict(lat=lat, lon=lon)] = EHI_sig*maximum(1, EHI_accl)
    hw.to_netcdf('test.nc')
if __name__ == "__main__":
    parametro1 = "./output/heatwave_opt2set.nc"#sys.argv[1]
    parametro2 = "./output/percentmax.nc"      #sys.argv[2]
    parametro3 = "./output/percentmin.nc"      #sys.argv[3]

    main(parametro1, parametro2, parametro3)

