#!/bin/bash
#Pasar como primer argumento la clave de la base de datos

#Asegurarse de que está activa la versión de ruby adecuada (2.3.0),
#Por ejemplo, ejecutar
#   rvm default ruby-2.3.0
#Y volver a abrir la terminal

#vuelvo a crear la tabla legales con el schema.
#mysql -u root -p legales < /home/guillermolvg/Descargas/legales/schema.sql

#Ejecutar el script de ruby en todos los archivos
cd ruby
echo "Ejecutando script de ruby..."
find ../DOCX/ -type f -exec ruby script.rb "{}" \;
cd ..

#Poner en archivos las tablas generadas por dicho script
echo "Exportando tablas"
echo "Nota, si no se pasó la clave como argumento del script, se solicitará a continuación 5 veces"
./export_ruby.sh $1

#Preprocesar archivos para su uso con los scripts de python
echo "Convirtiendo archivos a txt..."
python word.py
echo "Procesando con freeling..."
python freeling.py

#Crear directorio para los archivos de salida
mkdir tablas

#Generar entidades con script de python y combinarlas con las de ruby
echo "Generando entidades con algoritmo 2"
python entidades.py
echo "Combinando entidades encontradas y generando CSV"
python entidades_merge.py > tablas/entities.csv
echo "Limpiando tabla de alias y generando CSV"
python alias.py > tablas/aliases.csv

#Generar eventos
echo "Inicia generación de eventos"
for verb in solicitó otorgó emitió publicó presentó
do
    echo "Obteniendo eventos para $verb"
    python eventos.py $verb
done
cat out_*.csv > tablas/events.csv
#Cargar eventos y todas las entidades a la tabla de mysql
echo "Cargando eventos y entidades a la tabla de la BD"
mysql -u root -p$1 legales -e "LOAD DATA LOCAL INFILE 'tablas/events.csv' INTO TABLE events CHARACTER SET UTF8 FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' (fecha,verb,quien,que,donde,a_quien,doc_id,word,contexto)"
mysql -u root -p$1 legales -e "truncate entities"
mysql -u root -p$1 legales -e "LOAD DATA LOCAL INFILE 'tablas/entities.csv' INTO TABLE entities CHARACTER SET UTF8 FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' (id,name,type)"

#Convertir a CSV las tablas que quedan como tsv (documentos, artículos, ocurrencias)
echo "Convirtiendo a CSV tablas TSV"
tr "\\t" "," < docs_ruby.tsv > tablas/documents.csv
tr "\\t" "," < occurrences.tsv > tablas/occurrences.csv
tr "\\t" "," < articles.tsv > tablas/articles.csv
