# Description of code and your functions
The code may priorize make all necessary calculations in *Python* and *CDO*.
For python you will need pandas, numpy, scipy, xarray and alive-progress
All conected by *BASH* and running in Linux systems. 

==LINUX FIRST==

``` pip install pandas numpy scipy xarray alive-progress pyspark```

## To run the code

	./extremos.sh netcdf/tmax.nc 1990 90 15 [netcdf/pr.nc] [netcdf/tmin.nc] [netcdf/percenttmax.nc] [netcdf/percenttmin.nc]

All data need be with tmin name to minimum temperature values, tmax name to maximum temperature, lat to latitude values, lon to longitude values and time to 
datatime values 
the params inside [] are option that need only if the calculus need

- If the time values are in Kelvin, convert automatically to Celsius
- If coordenates names are latitude or longitude, change to lat and lon

**Output**: The output is a named 'heatwave_opt*set.nc' and * is the option of heatwave calculations

The paramns are:

1) it's the daily maximum temperature netcdf file complete, like (1961-2024)
2) it's the year that start the calculation of index
3) it's the percentil that is used in temperature relative calculations
4) it's number of days that are used like window calculation
5) it's the daily precipitation netcdf file, like (1961-2024)
6) it's the daily minimum temperature netcdf file complete, like (1961-2024)
7) it's the historic netcdf to construct tmax percent 
8) it's the historic netcdf to construct tmin percent


**The images are saved ar directory "imagens" and the data are saved in directory "dados"**

## ./output
1. <b> heatwave_opt$set.nc </b> is the file where $ is the option of heatwave, with heatwave data

## ./netcdf
#1. <b> tmax.nc </b> is the tmax temperatura for one latitude and longitude
#1. <b> tmin.nc </b> is the tmin temperatura for one latitude and longitude
#1. <b> pr.nc </b> is the precipitation for one latitude and longitude

## ./intern
1. <a href="./intern/spi.py"> spy.py</a> use the precipitaion to calculate the spi index

2. <a href="./intern/heatwave_opt1set.nc">heatwave_opt1set.py</a>  calculate the heatwave by year, season and extention considering World Meteorogical Organization definition of Heatwave
3. <a href="./intern/heatwave_opt2set.nc">heatwave_opt1set.py</a>  calculate the heatwave by year, season and extention considering World Meteorogical Organization definition of Heatwave using min temperature
4. <a href="./intern/heatwave_opt4set.nc.py"> heatwave_opt4set..py </a> open the file in ./intern/heatwave3ormore.py, that create the heatwave files considering heatwaves when has 3 hotdays using maximum temperature

5. <a href="./intern/geirinhas.py">geirinhas.py</a>  calculate the index based at gueirinhas metodology
6. <a href="./intern/plot_spi.py">plot_spi.py</a> create the graph of spi in html 
7. <a href="./intern/plot_linear_tmaxtmin_heatwave.py">plot_linear_tmaxtmin_heatwave.py</a> create the graph of heatwave of tmaxtmin heatwaves
8. <a href="./intern/anomaly.py">anomaly.py</a> create the graph of temperature anomaly of each heatwave

<b> Support</b>

9. <a href="./intern/txttonetcdf.py"> txttonetcdf.py </a> open the file in ./dados/input.csv, that can be updated with excel and after to convert to netcdf
10. <a href="./intern/expand_reference.py"> Expand reference.py</a> change the file expanding the latitude and longitude
11. <a href="./intern/parquet2netcdf.py"> parquet2netcdf.py</a> This function make the txt file chenge to netcdf
12. <a href="./intern/support.py"> support.py</a> have all important functions
13. <a href="./intern/preload_pr.py"> preload_pr.py</a> Load files and change configuration of precipitation data to avoid errors
14. <a href="./intern/preload_tmax.py"> preload_tmax.py</a> Load files and change configuration of maximum temperature data to avoid errors
15. <a href="./intern/preload_tmin.py"> preload_tmin.py</a> Load files and change configuration of minimum temperature data to avoid errors

## Reference
Geirinhas, João & Russo, Ana & Libonati, Renata & Sousa, Pedro & Miralles, Diego & Trigo, Ricardo. (2021). <a href="https://iopscience.iop.org/article/10.1088/1748-9326/abe0eb">Recent increasing frequency of compound summer drought and heatwaves in Southeast Brazil. Environmental Research Letters</a>. 16. 10.1088/1748-9326/abe0eb. 

<a hef="https://www.undrr.org/understanding-disaster-risk/terminology/hips/mh0047#:~:text=It%20defines%20heatwaves%20as%2C%20%E2%80%9Cperiods,WMO%20and%20WHO%2C%202015)."> United Nations Office for Disaster Rist Reduction</a>, Accessed 3 mar 2024

Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022). <a href="https://github.com/AlexandreCandidoXavier/BR-DWGD">New improved Brazilian daily weather gridded data (1961–2020) </a>. International Journal of Climatology, 42(16), 8390– 8404. https://doi.org/10.1002/joc.7731

<p>Intense Heat Wave</p>
John R. Nairn 1,* and Robert J. B. Fawcett. (2013). <a href="https://www.researchgate.net/publication/270292252_The_Excess_Heat_Factor_A_Metric_for_Heatwave_Intensity_and_Its_Use_in_Classifying_Heatwave_Severity">The Excess Heat Factor: A Metric for Heatwave Intensity and Its Use in Classifying Heatwave Severity </a>. International Journal of Environmental Research and Public Health (IJERPH)

