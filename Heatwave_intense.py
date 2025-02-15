import pandas as pd
import numpy as np

def EHF(time_series:np.ndarray, time_series_datetime:np.ndarray,time_series_heatewave:np.ndarray, percent:np.ndarray) -> np.ndarray:
    #time_series: Array with the value of variable for each day
    #time_series_datetime: Array with the date of variable for each day
    #time_series_heatwave
    #percent: Array with the value with percent for each day of reference

    #Excess Heat Factor
    time_series_datetime = pd.todate(time_series_datetime)
    EHI_sig = np.zeros(time_series_datetime.size)
    EHI_accl = np.zeros(time_series_datetime.size)
    
    for i in time_series_datetime:
        if time_series_heatewave[i] == 1:#This day start a Heatwave
            EHI_sig[i] = time_series[i, i+3].sum()/3 + percent[time_series_datetime[i].dayofyear] #calcule EHI sig
            EHI_accl[i] = time_series[i, i+3].sum()/3 + time_series[i-30, i].sum()/30 #calcule EHI accl
        else:
            EHI_sig[i] = 0
            EHI_accl[i] = 0

    return EHI_sig @ np.max(EHI_accl, np.ones(EHI_accl.size))

    
            
    
time_series_heatwave = pd.read_csv('./dados/Heatwaves_complete.csv').loc[:, 'cdh']
EHC()
