# League of Legends
## Última entrega Proyecto Almacenamiento de Datos
Todo hecho en Windows usando Python 3.5.2 (importante para ciertas líneas de código), con MrJob 0.6.0 y usando Riot API:

## Scripts:

**RiotAPI.py**: Este es el script que se utiliza para acumular los datos de los partidos de League of Legends.

**RiotConstants.py**: Este script mantiene los datos estáticos que sirven para hacer llamadas al API de Riot y escoger el apropiado

**RiotPruning.py**: Este script es usado para deshacer de los datos duplicados que pueden aparecer en la base de datos.

**RiotPlotCharacters.py**: Este script se encarga de procesar todos los datos. Con el mapper y reducer necesario. Incluye las formas de graficar los datos obtenidos y la generación de los archivos csv con algunas modificaciones.

**RiotWeightConstants.py**: Este script mantiene los datos estáticos de los pesos designados a cada elemento a evaluar.

**csv_data.py**: Este script genera un archivo csv en base a lots distintos roles y lanes que generalmente usa cada personaje.

## JSON:

**matches1/2/3/4/5.json**: Estos son los archivos que se usaban antiguamente como partidos bases de donde partir

**champions_data.json**: Estos son los datos de los personajes disponibles actualmente en el juego. Solamente contiene los nombres porque es lo único necesario

**pro_matches.json**: Estos son los partidos nuevos que se utilizaron para los datos nuevos, para así tener datos más recientes y relevantes a alto nivel.

## CSV:

**champ_strategies_p.csv**: Los datos de las estrategias de cada personaje con los datos viejos, cada número representando un role ó lane de forma específica

**champ_strategies_preseason.csv**: Los datos de las estrategias de cada personaje con los datos nuevos, cada número representando un role ó lane de forma específica