#!/bin/bash
# ./extremos [-c] tmax.nc year percentile window pr.nc tmin.nc [tmax_ref.nc tmin_ref.nc]
# -c: flag opcional para modo compacto/silencioso
# 1: daily maximum temperature netcdf file (1961-2024)
# 2: year that start the calculation of index
# 3: percentile used in temperature relative calculations
# 4: number of days used for window calculation
# 5: daily precipitation netcdf file (1961-2024)
# 6: daily minimum temperature netcdf file (1961-2024)
# 7: historic netcdf to construct tmax percent (opcional)
# 8: historic netcdf to construct tmin percent (opcional)

# Processar flag -c sem alterar ordem dos parâmetros principais
C_FLAG=false
MAIN_ARGS=()

# Separete flags per arguments
for arg in "$@"; do
    if [[ "$arg" == "-c" ]]; then
        C_FLAG=true
    else
        MAIN_ARGS+=("$arg")
    fi
done

# If -c is active, silence mode
if $C_FLAG; then
    exec 3>&2  # Salva stderr
    exec 2>/dev/null  # Redireciona stderr para /dev/null
fi

function Percentil_max() { # This code calculate the percentil about minimum temperature serie
  #1 it's the daily maximum temperature netcdf file complete, like (1961-2024)
  #2 it's the year that start the calculation of index
  #3 it's the percentil that is used in temperature relative calculations
  #4 it's number of days that are used like window calculation
  #5 it's the daily precipitation netcdf file, like (1961-2024)

  # Percentil tmax.nc year percentil window

  #Finding the period of years at file
  if ! $C_FLAG; then echo "Creating percent of maximum temperature file"; fi
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=${year[1]}
  ymax=(${year[-1]})
  cdo selyear,${ymin}/$((${2}+1))  $1 historical_tmax.nc >>/dev/null
  #creating the percent period of reference
  cdo ydrunpctl,$3,$4 historical_tmax.nc -ydrunmin,$4 historical_tmax.nc -ydrunmax,$4 historical_tmax.nc ./percentmax.nc >>/dev/null
  if ! $C_FLAG; then echo "calculated percentile of maximum temperature"; fi
}

function Percentil_min() { # Calculate the percentil about maximum temperature serie
  #1 it's the daily minimum temperature netcdf file complete, like (1961-2024)
  #2 it's the year that start the calculation of index
  #3 it's the percentil that is used in temperature relative calculations
  #4 it's number of days that are used like window calculation
  #5 it's the daily precipitation netcdf file, like (1961-2024)

  # Percentil tmax.nc year percentil window

  #Finding the period of years at file
  if ! $C_FLAG; then echo "Creating percentil of minimum temperature"; fi
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})
  cdo selyear,${ymin}/$((${2}+1)) $1 historical_tmin.nc >>/dev/null
  #Calculating percentil
  cdo ydrunpctl,$3,$4 historical_tmin.nc -ydrunmin,$4 historical_tmin.nc -ydrunmax,$4 historical_tmin.nc percentmin.nc >>/dev/null
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
    if ! $C_FLAG; then echo "Unit is Kelvin. Converting to Celsius..."; fi
    tmpfile=$(mktemp)
    cdo -chunit,K,Celsius -subc,273.15 "$1" "$tmpfile" && mv "$tmpfile" "$1"
  fi
}

# Verificar se há argumentos principais suficientes
if [[ ${#MAIN_ARGS[@]} -lt 5 ]]; then
    if ! $C_FLAG; then
        echo "Error: Insufficient arguments"
        echo "Usage: $0 [-c] tmax.nc year percentile window pr.nc [tmin.nc tmax_ref.nc tmin_ref.nc]"
        echo "Example: $0 -c netcdf/tmax.nc 1990 90 15 netcdf/pr.nc netcdf/tmin.nc"
    fi
    exit 1
fi

# Atribuir argumentos principais
TMAX_FILE="${MAIN_ARGS[0]}"
YEAR="${MAIN_ARGS[1]}"
PERCENTILE="${MAIN_ARGS[2]}"
MIN_DAYS="${MAIN_ARGS[3]}"
PR_FILE="${MAIN_ARGS[4]}"
TMIN_FILE="${MAIN_ARGS[5]:-}"  # Opcional
TMAX_REF="${MAIN_ARGS[6]:-}"   # Opcional
TMIN_REF="${MAIN_ARGS[7]:-}"   # Opcional

# Even show the user options
echo "Wich heatwave definition you will considerate?
		1 -> Consider the OMM definition of heatwve
		2 -> Consider the OMM definition with mininum temperature
		3 -> Consider the Gueirinhas definition and request precipitation file
		4 -> Consider 3 hotdays or more tmax to define heatwave
		5 -> Consider 3 hotdays or more to tmax and tmin to define heatwave"

read r

# Check user choice
if [[ ! "$r" =~ ^[1-5]$ ]]; then
    echo "Error: Invalid choice. Please select a number between 1 and 5."
    exit 1
fi

convertKelvin2Celsius $TMAX_FILE

# If is necessary, convert tmin
if [[ -n "$TMIN_FILE" && ($r -eq 2 || $r -eq 5) ]]; then
    convertKelvin2Celsius $TMIN_FILE
fi

mkdir temporary # make a new folder to group temporary files

if [ $r == 1 ]; then
  preload_tmax $TMAX_FILE
  if [ -z "$TMAX_REF" ]; then #if file tmax reference is't passed
    Percentil_max temporary/temporary_tmax.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
    if ! $C_FLAG; then echo "Creating heatwave data"; fi
    python3 intern/heatwave_opt1set.py temporary/temporary_tmax.nc ./percentmax.nc #Calculating heatwaves
    if ! $C_FLAG; then echo "Creating heatwave data"; fi
    tvar=$(cdo griddes ./percentmax.nc | grep "xsize" | awk '{print $3}')
    if [ ${tvar} ] > 1; then
      python3 intern/graph_heatwave_region.py temporary/temporary_tmax.nc heatwave_opt1set.nc
    fi
  else #if file is separeted in two
    python3 intern/heatwave_opt1set.py netcdf/tmax.nc $TMAX_REF #Create heatwave considering only tmax
  fi

elif [ $r == 2 ]; then
  if [ -z "$TMIN_FILE" ]; then
    echo "Error: Option 2 requires tmin.nc file (parameter 6)"
    exit 1
  fi
  preload_tmax_tmin $TMAX_FILE $TMIN_FILE
  if [ -z "$TMAX_REF" ]; then #if file tmax reference is't passed
    Percentil_max temporary/temporary_tmax.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
    Percentil_min temporary/temporary_tmin.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
    if ! $C_FLAG; then echo "Creating heatwave data"; fi
    python3 intern/heatwave_opt2set.py $2 temporary/temporary_tmax.nc temporary/temporary_tmin.nc ./percentmax.nc ./percentmin.nc # Create heatwave considering tmax and tmin
    #python3 intern/graph_heatwave_region.py 1 heatwave_opt2set.nc

  else #if file is separeted in two
    if ! $C_FLAG; then echo "Creating heatwave data"; fi
    python3 intern/heatwave_opt2set.py $2 temporary/temporary_tmax.nc temporary/temporary_tmin.nc $TMAX_REF $TMIN_REF # Create heatwave considering tmax and tmin
  fi

elif [ $r == 3 ]; then
  if ! $C_FLAG; then echo "At development"; fi

elif [ $r == 4 ]; then
  preload_tmax $TMAX_FILE
  Percentil_max temporary/temporary_tmax.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
  if ! $C_FLAG; then echo "Creating heatwave data"; fi
  python3 intern/heatwave_opt4set.py temporary/temporary_tmax.nc ./percentmax.nc

elif [ $r == 5 ]; then
  if [ -z "$TMIN_FILE" ]; then
    echo "Error: Option 5 requires tmin.nc file (parameter 6)"
    exit 1
  fi
  preload_tmax_tmin $TMAX_FILE $TMIN_FILE
  Percentil_max temporary/temporary_tmax.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
  Percentil_min temporary/temporary_tmin.nc $(($YEAR - 1)) $PERCENTILE $MIN_DAYS $PR_FILE
  if ! $C_FLAG; then echo "Creating heatwave data"; fi
  python3 intern/heatwave3ormoretmaxtmin.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc
fi

#Organize files in directories
if [ ! -d img ]; then
  mkdir img
fi
mv *.png img 2>/dev/null

if [ ! -d output ]; then
  mkdir output
fi
#Remove trash data
mv heatwave*.nc output 2>/dev/null
mv historical*.nc output 2>/dev/null
mv percent*.nc output 2>/dev/null
rm -rf temporary

if $C_FLAG; then
    exec 2>&3
fi