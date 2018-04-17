# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
#------------------------------------------------------
# No recibe argumentos.
# Devuelve una lista de entidades etiquetadas con el NERC de FreeLing 4.0
#------------------------------------------------------
import subprocess
import os
import docx2txt
import re
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
client.drop_database('NERLegalesFL')
db = client.NERLegalesFL
collection = db.Entidades
try:
    os.remove("salidaFreeling.txt")
except FileNotFoundError:
    pass
path_docx = "Evaluacion/CorpusEval/Archivo"
for fname in os.listdir(path_docx):
    fullpath = os.path.join(path_docx, fname)
    print ("Archivo: " + fullpath + "\n")
    textoPlano = docx2txt.process(fullpath)
    with open("DOCX_txt/"+fname+".txt","w") as entrada:
        entrada.write(textoPlano)
    with open("DOCX_txt/"+fname+".txt","r") as entrada:
        salida = open("salidaFreeling.txt","a+")
        subprocess.call('analyzer_client 50005',stdin=entrada,stdout=salida,shell=True)
        salida.close()

with open ("salidaFreeling.txt","r") as entrada:
    listaEntidades = []
    lineasTexto = entrada.readlines()
    for line in lineasTexto:
        partes = line.split()
        if len(partes) == 4:
            if re.search("NP00.*?",partes[2]):
                listaEntidades.append(partes[0])

listaEntidades = set(listaEntidades)
for entidad in listaEntidades:
    db.collection.insert({"Nombre":entidad})
