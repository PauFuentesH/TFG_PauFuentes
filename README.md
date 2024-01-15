# Estudi de l'equilibri amb dospositiu IMU
Aquest repositori recull els arxius amb el codi per poder replicar els resultats presentats en el document PDF.

## Continguts:
#### dades_posturograf.py: 
Fitxer que s'encarrega de calcular les mètriques a partir de les fòrmules plantejades i comparar els resultats amb les mètriques reals. S'utilitza l'arxiu ./Fitxers_per_entrenar.
#### carregar_dades.py: 
Fitxer on es carreguen en un fitxer .csv els valors de l'acceleració màxima, el màxim del vector gravetat i el màxim desplaçament de les dades recollides pel dispositiu IMU de cada pacient. S'utilitza l'arxiu Mataro_postu_IMU. 
#### funcions.py: 
Fitxer que conté les funcions que utilitzen els fitxers 'dades_posturograf.py' i 'carregar_dades.py'.



