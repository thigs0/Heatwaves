# Description of code and your functions

The code may priorize make all necessary calculations in *Python* and *CDO*.
All conected by *BASH* and running in Linux systems. 

## To run the code

´´´python
./extremos.sh tmax.nc 1990 90 15 pr.nc´´´

The paramns are:

1) é o netcdf de temperatura máxima completo
2) é o ano que a partir dele calculamos o índice
3) é o percentil de temperatura que queremos calcular
4) são os dias que usamos como janela
5) é o netcdf de precipitação diária 

As imagens são salvas na pasta de imagens e os dados são salvos na pasta dados

./dados :
	Heatwave.csv é o arquivo com as ondas de calor anual
	Heatwaves_days.csv é o arquivo com maior período contínuo de ondas de calor 
	Heatwaves_complete.csv é o arquivo com cada dia, 1 se teve onda de calor nos próximos 3 dias, 0 se não
	season.csv é o arquivo com ondas de calor por estação, 1 de Nov-Fev, 2 de Mar-Mai, 3 de Jun-Ago, 4 Set-Nov
	kendall.csv é o arquivo com valores das ondas de calor para o teste de Mann-kendall


./intern :
	spi.py Usa o arquivo de precipitação para calcular o SPI
	HeatWave.py Calcula e salva as ondas de calor por ano, estação e prolongamento
	geirinhas.py Calcula os índices extremos com base na metodologia do gueirinhas
	linear.py Calcula as linhas lineares de tendência da heatweve e contínua
	linear_season.py Calcula as linhas lineares de tendência da heatwave das estações
	plot_spi.py controi o gráfico do spi em html 

