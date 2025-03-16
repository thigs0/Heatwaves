#!/bin/bash
#./extremos tmax.nc 1990 90 15 pr.nc
#1 é o netcdf de temperatura máxima completo
#2 é o ano que a partir dele calculamos o índice
#3 é o percentil de temperatura que queremos calcular
#4 é o dias que usamos como janela
#5 é o netcdf de precipitação diária
#6 é o netcdf da temperatura mínima se quiser ser passado

#Tendo um arquivo netcdf4 com as datas completas chamada df.nc,
#Com apenas uma variável de clima
#Se o arquivo passadofor txt, convertemos para netcdf

function Percentil_max() { # calcula o percentil de uma série temporal de temperatura mínima
  #1 é o netcdf4 de temperatura máxima
  #2 ano final de referência
  #3 é qual o percentil que queremos calcular
  #4 é o dias que usaremos como janela
  #5 é o netcdf de precipitação diária

  # Percentil tmax.nc year percentil window

  #Encontramos o período de anos do arquivo
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})
  cdo selyear,${ymin}/${2} $1 tmax_ref.nc >>/dev/null
  cdo selyear,$(($2 + 1))/${ymax} $1 tmax_f.nc >>/dev/null #O arquivo nc com as temperatpuros no período que avaliamos
  cdo selyear,${ymin}/${2} $5 pr_ref.nc >>/dev/null

  #Calcula o percentiu do período de referência
  cdo ydrunpctl,$3,$4 tmax_ref.nc -ydrunmin,$4 tmax_ref.nc -ydrunmax,$4 tmax_ref.nc percentmax.nc >>/dev/null
  rm tmax_ref.nc
}

function Percentil_min() { # calcula o percentil de uma série temporal de temperatura mínima
  #1 é o netcdf4 de temperatura mínima
  #2 ano final de referência
  #3 é qual o percentil que queremos calcular
  #4 é o dias que usaremos como janela
  #5 é o netcdf de precipitação diária

  # Percentil tmax.nc year percentil window

  #Encontramos o período de anos do arquivo
  year="$(cdo -S showyear $1 | head -n 4)"
  year=($year)
  ymin=(${year[0]})
  ymax=(${year[-1]})
  cdo selyear,${ymin}/${2} $1 tmax_ref.nc >>/dev/null
  cdo selyear,$(($2 + 1))/${ymax} $1 tmax_f.nc >>/dev/null #O arquivo nc com as temperatpuros no período que avaliamos
  cdo selyear,${ymin}/${2} $5 pr_ref.nc >>/dev/null

  #Calcula o percentiu do período de referência
  cdo ydrunpctl,$3,$4 tmax_ref.nc -ydrunmin,$4 tmax_ref.nc -ydrunmax,$4 tmax_ref.nc percentmin.nc >>/dev/null
  rm tmax_ref.nc
}

function SPI() {
  #1 é o netcdf de precipitação diária
  python3 intern/spi.py $5 #Calcula o índice spi e salva em spi.nc
}

function percentagem() {
  #Ainda em construção
  #Calcula o termo relativo de crescimento

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

echo "Wich heatwave definition you will considerate?
		1 -> Consider the OMM definition of heatwve
		2 -> Consider the OMM definition with mininum temperature
		3 -> Consider the Gueirinhas definition and request precipitation file
		4 -> Consider 3 hotdays and tmax to define heatwave
		5 -> Consider 3 hotdays or more to tmax and tmin to define heatwave"

read r
if [ $r == 1 ]; then
  Percentil_max $1 $(($2 - 1)) $3 $4 $5 >>/dev/null
  python3 intern/HeatWave.py netcdf/tmax.nc #Gera os dados de heatwave

elif [ $r == 2 ]; then
  echo "Construindo o percentil da temperatura máxima"
  Percentil_max $1 $(($2 - 1)) $3 $4 $5
  echo "Construindo o percentil da temperatura mínima"
  Percentil_min $6 $(($2 - 1)) $3 $4 $5
  echo "Gerando os dados de ondas de calor"
  python3 intern/tmaxtmin_heatwave.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc # gera dados considerando max e min
  python3 intern/cumulative_heat.py                                                                 #gera os dados acumulados de cada onda de calor

  #python3 intern/plot_cummulative.py
  python3 intern/anomaly.py

elif [ $r == 3 ]; then
  spi=$(SPI $5)
  python3 intern/geirinhas.py netcdf/tmax.nc -0.5 cdh_-05.csv # Gera dados considerando max e precipitação
  python3 intern/plot_spi.py                                  #gera os dados de spi

elif [ $r == 4 ]; then
  echo "Construindo o percentil da temperatura máxima"
  Percentil_max $1 $(($2 - 1)) $3 $4 $5
  echo "Gerando os dados de ondas de calor"

  python3 intern/heatwave3ormore.py netcdf/tmax.nc ./percentmax.nc # Gera dados considerando max e precipitação
elif [ $r == 5 ]; then
  echo "Construindo o percentil da temperatura máxima"
  Percentil_max $1 $(($2 - 1)) $3 $4 $5
  echo "Construindo o percentil da temperatura mínima"
  Percentil_min $6 $(($2 - 1)) $3 $4 $5
  echo "Gerando os dados de ondas de calor"

  python3 intern/heatwave3ormoretmaxtmin.py netcdf/tmax.nc netcdf/tmin.nc ./percentmax.nc ./percentmin.nc # Gera dados considerando max e precipitação

fi

#Gera regressão linear e teste de tendência
python3 intern/plot.py
python3 intern/linear_season.py

#Organiza em pastas
if [ ! -d imagens ]; then
  mkdir imagens
fi
mv *.png imagens

if [ ! -d dados ]; then
  mkdir dados
fi
mv *.csv dados

#Remome trash data
rm *.nc
