#!/bin/bash
# Script para obtener las tablas del script de ruby.
# Debe haberse ejecutarse primero ruby/script.rb sobre todos los archivos

mysql -u root -p$1 legales -e "select * from occurrences" -B > occurrences.tsv
mysql -u root -p$1 legales -e "select id,name from entities" -B > entidades_ruby.tsv
mysql -u root -p$1 legales -e "select * from aliases" -B > aliases_ruby.tsv
mysql -u root -p$1 legales -e "select * from articles" -B > articles.tsv
mysql -u root -p$1 legales -e "select * from documents" -B > docs_ruby.tsv
