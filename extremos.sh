#!/bin/bash
#./extremos tmax.nc 1990 90 15 pr.nc
#1 é o netcdf de temperatura máxima completo
#2 é o ano que a partir dele calculamos o índice
#3 é o percentil de temperatura que queremos calcular
#4 é o dias que usamos como janela
#5 é o netcdf de precipitação diária

#Tendo um arquivo netcdf4 com as datas completas chamada df.nc,
#Com apenas uma variável de clima

function Percentil(){
	#1 é o netcdf4 de temperatura máxima
	#2 ano final de referência
	#3 é qual o percentil que queremos calcular
	#4 é o dias que usaremos como janela
	#5 é o netcdf de precipitação diária

	# Percentil tmax.nc year percentil window 

	#Encontramos o período de anos do arquivo
	year="$(cdo -S showyear $1 | head -n 4)"; year=($year);
	ymin=(${year[0]}); ymax=(${year[-1]})
	cdo selyear,${ymin}/${2} $1 tmax_ref.nc
	cdo selyear,$(($2+1))/${ymax} $1 tmax_f.nc #O arquivo nc com as temperatpuros no período que avaliamos
	cdo selyear,${ymin}/${2} $5 pr_ref.nc

	#Calcula o percentiu do período de referência
	cdo ydrunpctl,$3,$4 tmax_ref.nc -ydrunmin,$4 tmax_ref.nc -ydrunmax,$4 tmax_ref.nc percent.nc
	rm tmax_ref.nc
}

function SPI(){
	#1 é o netcdf de precipitação diária
	python3 intern/spi.py $1  #Calcula o índice spi e salva em spi.nc
}

function percentagem(){
	#Ainda em construção
	#Calcula o termo relativo de crescimento

	year="$(cdo -S showyear $1 | head -n 4)"; year=($year);
	ymin=(${year[0]}); ymax=(${year[-1]})
	
	cdo selyear,1980/1998 spi.nc hist.nc
	cdo sum hist.nc soma_hist.nc
	cdo selyear,1999/${ymax} $1 ref.nc
	cdo sum ref.nc soma_ref.nc

	dif=$((soma_hist.nc-soma_ref.nc))
	soma=$((soma_hist.nc+soma_ref.nc))
	div=$((dif/soma))
	
}
Percentil $1 $(($2-1)) $3 $4 $5
spi=$(SPI $5)

echo $(python3 intern/geirinhas.py tmax_f.nc -0.5 cdh_-05.csv)
python3 intern/HeatWave.py tmax_f.nc #Gera os dados de heatwave
python3 intern/plot_spi.py #gera os dados de spi

#Gera regressão linear e teste de tendência
python3 intern/linear.py 

#Organiza em pastas
mkdir imagens
mv *.png imagens
mkdir dados
mv *.csv dados

# Calculo do percentual
rm pr_ref.nc percent.nc tmax_f.nc


