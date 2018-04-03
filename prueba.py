# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
#------------------------------------------------------
# No recibe argumentos.
# Busca los archivos en DOCX_txt, y a cada uno le saca una lista de alias, los cuales
# asocia a una entidad.
#------------------------------------------------------
import docx2txt
import os
import sys
import re
import csv

nombre = input("Archivo: ")
indice = int(input("Índice: "))
fullpath = "DOCX/" + nombre + ".docx"
print ("Archivo: " + fullpath + "\n")
textoPlano = docx2txt.process(fullpath)
print(textoPlano[indice:indice+100])
