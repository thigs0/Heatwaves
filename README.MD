# Description of code and your functions

The code may priorize make all necessary calculations in *Python* and *CDO*.
All conected by *BASH* and running in Linux systems. 

## To run the code

	./extremos.sh tmax.nc 1990 90 15 pr.nc

The paramns are:

1) it's the daily maximum temperature netcdf file complete
2) it's the year that start the calculation of index
3) it's the percentil that is used in temperature relative calculations
4) it's number of days that are used like window calculation
5) it's the daily precipitation netcdf file 

**The images are saved ar directory "imagens" and the data are saved in directory "dados"**

## ./dados
1. Heatwave.csv is the file with annual heatwaves
2. Heatwaves_days.csv is the file with the maximum continum period of heatwave 
3. Heatwaves_complete.csv is the file that say the dayly period of heatwaves. 0 don't have heatwave, 1 have heatwaves next 3 days
4. season.csv if the file with daily heatwave, but separete by season, colum:1 of Nov-Fev, colum:2 of Mar-Mai, colum:3 of Jun-Ago, colum:4 of Set-Nov
5. kendall.csv is the file with heatwaves values for  mann-Kendall test and linear regression


## ./intern
1. spi.py use the precipitaion to calculate the spi index
2. HeatWave.py calculate the heatwave by year, season and extention
3. geirinhas.py calculate the index based at gueirinhas metodology
4. linear.py calculate the linear regresion and Mann-Kendall test for heatwaves
5. linear_season.py calculate linear regression and Mann-Kendall test  for season heatwaves
6. plot_spi.py create the graph of spi in html 

