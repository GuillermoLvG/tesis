# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# Script que limpia la tabla de alias
#---------------------------------------------------------------------------
# Deja solo lo que está entre comillas y puede hacer filtrados adicionales.
# Debe haberse ejecutado primero export_ruby.rb
#---------------------------------------------------------------------------
import re
comillas = "“(.*?)”"
with open("aliases_ruby.tsv") as f:
    f.readline()
    for line in f:
        line = line.strip()
        id,doc,ent,line = line.split("\t")
        if "centavos" in line:
            continue
        line = line.replace("en lo sucesivo", "")
        line = line.replace("de", "")
        line = line.replace("la", "")
        line = line.replace("el", "")
        line = line.replace(",", "")
        line = line.replace('"""', "”")
        line = line.replace('""', "“")
        line = line.replace("'", "")
        line = line.replace('"', '')
        line = line.replace('”', '')
        line = line.replace('“', '')
        line = line.strip()
        m = re.search(comillas, line)
        if m:
            print ",".join([id,doc,ent,m.group(1)])
        else:
            print ",".join([id,doc,ent,line])
