# -*- coding: utf-8 -*-
#----------------------------------------------------------------
# Script que crea el archivo csv final de entidades
#----------------------------------------------------------------
# Combina las que se obtienen del script de ruby y las del de python, les pone tipo (ley, organización, otro) y un ID
# Debe ser ejecutado antes de ejecutar el script de eventos.
# No recibe argumentos, pero debe haberse corrido previamente el script export_ruby.sh
#----------------------------------------------------------------
import re

ruby = set()
ids_ruby = {}
max_id_ruby = 0
with open("entidades_ruby.tsv") as f:
    for line in f:
        if line.startswith("id"):
            continue
        id_ruby, entidad_ruby = line.strip().split("\t")
        id_ruby = int(id_ruby)
        if entidad_ruby not in ruby:
            ruby.add(entidad_ruby)
            ids_ruby[entidad_ruby] = id_ruby
        if max_id_ruby < id_ruby:
            max_id_ruby = id_ruby

python = []
ids_python = {}
id_seq = max_id_ruby + 1
with open("out_entities") as f:
    for line in f:
        python = line.strip().replace("_", " ")
        if python in ids_ruby:
            ids_python[python] = ids_ruby[python]
        else:
            ids_python[python] = id_seq
            id_seq += 1

for entity,id in ids_python.iteritems():
    name = entity.lower()
    palabras_ley = ["ley", "constitución", "estatuto", "código"]
    for palabra in palabras_ley:
        if palabra in name:
            tipo = 'Ley'
            break
    else:
        palabras_org = ["ssion", "srldecv", "sadecv", "sabdecv", "sapidecv", "instituto", "ía (.*)? de", "ión (.*)? de", " y "]
        for palabra in palabras_org:
            if re.search(palabra, name):
                tipo = 'Organización'
                break
        else:
            tipo = "Otro"
        
    print ",".join([str(id),entity.replace(",",""),tipo])
