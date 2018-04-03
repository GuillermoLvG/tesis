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
	if len(candidato.split()) == 1:
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
			resultado = {"Nombre": candidato, "Archivos": {fname.replace(".docx",""): {"indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } } }
			resultados.append(resultado)
	return resultados

def insertarEnBD(resultado):
	'''
	Si ya existe la entidad en la base de datos, se actualiza con la nueva información

	1.- Obtener el diccionario de "Archivos" que viene en el resultado
	2.- Obtener el diccionario que ya está guardado en la base de datos (si existe)
	3.- Si sí existe en la base datos, entonces junto los dos diccionarios y los guardo en archivos
	4.- Hago update, o creo el documento, en la base de datos.
	'''
	archivoDB = dict()
	archivo = resultado["Archivos"]
	archivoBD = collection.find_one({"Nombre":resultado["Nombre"]},{"Archivos":1})
	if archivoBD:
		archivoBD = archivoBD["Archivos"]
		archivo = {**archivo, **archivoBD}
	entidad = collection.find_one_and_update({"Nombre": resultado["Nombre"]},{"$set": {"Archivos": archivo}},upsert=True)

def Main():
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
				insertarEnBD(resultado)

Main()
