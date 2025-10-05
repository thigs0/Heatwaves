#!/bin/bash
#./extremos tmax.nc 1990 90 15 pr.nc
#1 it's the daily maximum temperature netcdf file complete, like (1961-2024)
#2 it's the year that start the calculation of index
#3 it's the percentil that is used in temperature relative calculations
#4 it's number of days that are used like window calculation
#5 it's the daily precipitation netcdf file, like (1961-2024)
#6 it's the daily minimum temperature netcdf file complete, like (1961-2024)
#7 it's the historic netcdf to construct tmax percent
#8 it's the historic netcdf to construct tmin percent

#To this code, each file need has only one climatic variable

function Percentil_max() { # This code calculate the percentil about minimum temperature serie
  #1 it's the daily maximum temperature netcdf file complete, like (1961-2024)
  #2 it's the year that start the calculation of index
  #3 it's the percentil that is used in temperature relative calculations
  #4 it's number of days that are used like window calculation
  #5 it's the daily precipitation netcdf file, like (1961-2024)

  # Percentil tmax.nc year percentil window

  #Finding the period of years at file
  echo "Creating percent of maximum temperature file"
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})
  cdo selyear,${ymin}/${2} $1 heatwave_ref.nc >>/dev/null
  cdo selyear,$(($2 + 1))/${ymax} $1 heatwave_f.nc >>/dev/null #File .nc with temperature at period to avaliate
  cdo selyear,${ymin}/${2} $5 pr_ref.nc >>/dev/null

  #creating the percent period of reference
  cdo ydrunpctl,$3,$4 heatwave_ref.nc -ydrunmin,$4 heatwave_ref.nc -ydrunmax,$4 heatwave_ref.nc percentmax.nc >>/dev/null
  rm heatwave_ref.nc
}

function Percentil_min() { # Calculate the percentil about maximum temperature serie
  #1 it's the daily minimum temperature netcdf file complete, like (1961-2024)
  #2 it's the year that start the calculation of index
  #3 it's the percentil that is used in temperature relative calculations
  #4 it's number of days that are used like window calculation
  #5 it's the daily precipitation netcdf file, like (1961-2024)

  # Percentil tmax.nc year percentil window

  #Finding the period of years at file
  echo "Creating percentil of minimum temperature"
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})
  cdo selyear,${ymin}/${2} $1 heatwave_ref.nc >>/dev/null
  cdo selyear,$(($2 + 1))/${ymax} $1 heatwave_f.nc >>/dev/null #File .nc with temperature at period to avaliate
  cdo selyear,${ymin}/${2} $5 pr_ref.nc >>/dev/null

  #Calculating percentil
  cdo ydrunpctl,$3,$4 heatwave_ref.nc -ydrunmin,$4 heatwave_ref.nc -ydrunmax,$4 heatwave_ref.nc percentmin.nc >>/dev/null
  rm heatwave_ref.nc
}

function SPI() {
  #1 it's the daily precipitation netcdf file, like (1961-2024)
  python3 intern/spi.py $5 #Calculate the SPI index and save with name "spi.nc"
}

function percentagem() {
  #At development
  #calculate the relative term

  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})

  cdo selyear,1980/1998 spi.nc hist.nc >>/dev/null
  cdo sum hist.nc soma_hist.nc >>/dev/null
  cdo selyear,1999/${ymax} $1 ref.nc >>/dev/null
  cdo sum ref.nc soma_ref.nc >>/dev/null

  dif=$((soma_hist.nc - soma_ref.nc))
  soma=$((soma_hist.nc + soma_ref.nc))
  div=$((dif / soma))

}
function convertKelvin2Celsius() { # if argument file is Kelvin, converto to celsius
  unidade=$(cdo showunit "$1" 2>/dev/null | head -n 1 | tr -d '[:space:]')
  if [ "$unidade" = "K" ]; then
    echo "Unit is Kelvin. Converting to Celsius..."
    tmpfile=$(mktemp)
    cdo -chunit,K,Celsius -subc,273.15 "$1" "$tmpfile" && mv "$tmpfile" "$1"
  fi
}

echo "Wich heatwave definition you will considerate?
		1 -> Consider the OMM definition of heatwve
		2 -> Consider the OMM definition with mininum temperature
		3 -> Consider the Gueirinhas definition and request precipitation file
		4 -> Consider 3 hotdays and tmax to define heatwave
		5 -> Consider 3 hotdays or more to tmax and tmin to define heatwave"

read r

convertKelvin2Celsius $1
convertKelvin2Celsius $6

if [ $r == 1 ]; then
  if [ -z "$7" ]; then #if file tmax reference is't passed
    Percentil_max $1 $(($2 - 1)) $3 $4 $5
    echo "Creating heatwave data"
    python3 intern/heatwave.py netcdf/tmax.nc ./percentmax.nc #Calculating heatwaves

    echo "Creating heatwave data"
    python3 intern/tmaxtmin_heatwave.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc # Create heatwave considering tmax and tmin
    python3 intern/cumulative_heat.py                                                                 #generate cumumulative number of heatwaves

    #python3 intern/plot_cummulative.py
    python3 intern/anomaly.py

  else                                           #if file is separeted in two
    python3 intern/heatwave.py netcdf/tmax.nc $7 #Create heatwave considering only tmax
  fi

elif [ $r == 2 ]; then
  if [ -z "$7" ]; then #if file tmax reference is't passed
    Percentil_max $1 $(($2 - 1)) $3 $4 $5
    Percentil_min $6 $(($2 - 1)) $3 $4 $5
    echo "Creating heatwave data"
    python3 intern/tmaxtmin_heatwave.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc # Create heatwave considering tmax and tmin
    python3 intern/cumulative_heat.py                                                                 #generate cumumulative number of heatwaves

    #python3 intern/plot_cummulative.py
    python3 intern/anomaly.py
  else #if file is separeted in two
    echo "Creating heatwave data"

    python3 intern/tmaxtmin_heatwave.py netcdf/tmax.nc netcdf/tmin.nc $7 $8 # Create heatwave considering tmax and tmin
    python3 intern/cumulative_heat.py                                       #generate cumumulative number of heatwaves

    #python3 intern/plot_cummulative.py
    python3 intern/anomaly.py
  fi

elif [ $r == 3 ]; then
  spi=$(SPI $5)
  python3 intern/geirinhas.py netcdf/tmax.nc -0.5 cdh_-05.csv # Create heatwaves considering tmax and pecipitation (spi file)
  python3 intern/plot_spi.py                                  #Plot SPI data

elif [ $r == 4 ]; then
  Percentil_max $1 $(($2 - 1)) $3 $4 $5
  echo "Creating heatwave data"

  python3 intern/heatwave3ormore.py netcdf/tmax.nc ./percentmax.nc # Create heatwaves considering tmax and pecipitation (spi file)
elif [ $r == 5 ]; then
  Percentil_max $1 $(($2 - 1)) $3 $4 $5
  Percentil_min $6 $(($2 - 1)) $3 $4 $5
  echo "Creating heatwave data"

  python3 intern/heatwave3ormoretmaxtmin.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc # Create heatwaves considering tmax and pecipitation (spi file)

fi

#Gera regressão linear e teste de tendência
python3 intern/plot.py
#python3 intern/linear_season.py

#Organize files in directories
if [ ! -d imagens ]; then
  mkdir imagens
fi
mv *.png imagens

if [ ! -d dados ]; then
  mkdir dados
fi
mv *.csv dados

#Remove trash data
rm *.nc
