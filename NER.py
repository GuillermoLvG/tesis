# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
#------------------------------------------------------
# No recibe argumentos.
# Busca en los archivos, entidades nombradas utilizando expresiones regulares.
# Inserta las entidades encontradas en una base de datos.
#------------------------------------------------------
import docx2txt
import os
import sys
import re
import csv
from NERalias import insertarEnBD
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.NERLegales
collection = db.Entidades
path_docx = "DOCX"

def limpiarCadena(string):
	'''
	Recibe una cadena, devuelve una cadena

	Reemplaza lo que sea necesario en la cadena.
	'''
	string = string.strip()
	string = string.replace(",","")
	return string
def filtroCandidatos(candidato):
	if len(candidato.split()) != 1:
		return candidato
	return ""
def buscarEntidades(texto,fname):
	'''
	Recibe una cadena y busca en ella una expresión regular que devuelve candidatos a entidad nombrada.
	Devuelve la lista de candidatos.
	'''
	resultados = []
	expresion = r"\b(([A-Z][a-záéíóú]+ ?)+(((la|el|los|las|un|una|uno|unas|unos|y|con|de|del) )*([A-Z][a-záéíóú]+ ?)+)*((, )?| )?(S.A. de C.V.|S. de R.L. de C.V.)?)"
	regex = re.compile(expresion)
	matches = regex.finditer(texto)
	for match in matches:
		candidato = limpiarCadena(match.group())
		candidato = filtroCandidatos(candidato)
		if candidato:
			indiceOcurrencia = match.start()
			Regla = "Expresión Regular"
			resultado = {"Nombre": candidato, "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } }
			resultados.append(resultado)
	return resultados
def MainNER():
	'''
	Flujo inicial del programa
	'''
	for fname in os.listdir(path_docx):
		fullpath = os.path.join(path_docx, fname)
		print ("Archivo: " + fullpath + "\n")
		textoPlano = docx2txt.process(fullpath)
		resultados = buscarEntidades(textoPlano,fname)
		if resultados:
			for resultado in resultados:
				print(resultado["Nombre"])
				insertarEnBD(resultado)
