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
  ymin=${year[1]}
  ymax=(${year[-1]})
  cdo selyear,${ymin}/${2} $1 heatwave_ref.nc >>/dev/null
  cdo selyear,$(($2 + 1))/${ymax} $1 heatwave_f.nc >>/dev/null #File .nc with temperature at period to avaliate
  cdo selyear,${ymin}/${2} $5 pr_ref.nc >>/dev/null

  #creating the percent period of reference
  cdo ydrunpctl,$3,$4 heatwave_ref.nc -ydrunmin,$4 heatwave_ref.nc -ydrunmax,$4 heatwave_ref.nc ./percentmax.nc >>/dev/null
  echo "calculated percentile of maximum temperature"
  rm heatwave_ref.nc heatwave_f.nc pr_ref.nc
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
  rm heatwave_ref.nc heatwave_f.nc pr_ref.nc
}

function preload_tmax_tmin() { # This code load file at temporary directory and chanhe some paramns
  python3 intern/preload_tmax.py $1
  python3 intern/preload_tmin.py $2
}

function preload_tmax(){ #This code load file at temporary directory and chanhe some paramns
  python3 intern/preload_tmax.py $1
}

function preload_tmin(){ #This code load file at temporary directory and chanhe some paramns
  python3 intern/preload_tmin.py $1
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
		4 -> Consider 3 hotdays or more tmax to define heatwave
		5 -> Consider 3 hotdays or more to tmax and tmin to define heatwave"

read r

convertKelvin2Celsius $1
convertKelvin2Celsius $6

mkdir temporary

if [ $r == 1 ]; then
  preload_tmax $1
  if [ -z "$7" ]; then #if file tmax reference is't passed
    Percentil_max temporary/temporary_tmax.nc $(($2 - 1)) $3 $4 $5
    echo "Creating heatwave data"
    python3 intern/heatwave_opt1set.py temporary/temporary_tmax.nc ./percentmax.nc #Calculating heatwaves
    echo "Creating heatwave data"
    tvar=$(cdo griddes ./percentmax.nc | grep "xsize" | awk '{print $3}')
    if [ ${tvar} ] > 1; then
      python3 intern/graph_heatwave_region.py temporary/temporary_tmax.nc heatwave_opt1set.nc
    fi
  else                                                   #if file is separeted in two
    python3 intern/heatwave_opt1set.py netcdf/tmax.nc $7 #Create heatwave considering only tmax
  fi

elif [ $r == 2 ]; then
  preload_tmax_tmin $1 $6
  if [ -z "$7" ]; then #if file tmax reference is't passed
    Percentil_max temporary/temporary_tmax.nc $(($2 - 1)) $3 $4 $5
    Percentil_min temporary/temporary_tmin.nc $(($2 - 1)) $3 $4 $5
    echo "Creating heatwave data"
    python3 intern/heatwave_opt2set.py temporary/temporary_tmax.nc temporary/temporary_tmin.nc ./percentmax.nc ./percentmin.nc # Create heatwave considering tmax and tmin
    #python3 intern/graph_heatwave_region.py 1 heatwave_opt2set.nc

  else #if file is separeted in two
    echo "Creating heatwave data"
    python3 intern/heatwave_opt2set.py temporary/temporary_tmax.nc temporary/temporary_tmin.nc $7 $8 # Create heatwave considering tmax and tmin
  fi

elif [ $r == 3 ]; then
  echo "At development"

elif [ $r == 4 ]; then
  preload_tmax $1
  Percentil_max temporary/temporary_tmax.nc $(($2 - 1)) $3 $4 $5
  echo "Creating heatwave data"
  python3 intern/heatwave_opt4set.py temporary/temporary_tmax.nc ./percentmax.nc

elif [ $r == 5 ]; then
  preload_tmax_tmin $1 $6
  Percentil_max temporary/temporary_tmax.nc $(($2 - 1)) $3 $4 $5
  Percentil_min temporary/temporary_tmin.nc $(($2 - 1)) $3 $4 $5
  echo "Creating heatwave data"
  python3 intern/heatwave3ormoretmaxtmin.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc 
fi

#Organize files in directories
if [ ! -d img ]; then
  mkdir img
fi
mv *.png img

if [ ! -d output ]; then
  mkdir output
fi
#Remove trash data
mv heatwave*.nc output
rm -rf temporary
