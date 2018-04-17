# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
#------------------------------------------------------
# No recibe argumentos.
# Devuelve métricas de evaluación. freelingNER.py vs main.py
#------------------------------------------------------
import os
import re
import openpyxl
import xml.etree.ElementTree
from pymongo import MongoClient

#Gold Standard
doc = openpyxl.load_workbook('entities_55.xlsx')
sheet = doc['Sheet1']
entidades = []
for reng in range(1,73):
	entidades.append(sheet.cell(row=reng,column=1).value)

entidades = set(entidades)
entidades = list(entidades)
goldStandard = []
for entidad in entidades:
	goldStandard.append(entidad.lower())

#Resultado Freeling
client = MongoClient('localhost', 27017)
db = client.NERLegalesFL
collection = db.collection
result = collection.find({})
freelingResults = []
for element in result:
	freelingResults.append(element["Nombre"].replace("_"," ").lower())

#Calculo de precisión y exhaustividad
TP = 0
FP = 0
for element in freelingResults:
	if element in goldStandard:
		TP = TP + 1
	else:
		FP = FP + 1
precision = (TP/(TP+FP))*100
FN = 0
for element in goldStandard:
	if element not in freelingResults:
		FN = FN + 1
recall = (TP/(TP+FN))*100

print("Freeling")
print("Precision: " + str(precision))
print("Recall: " + str(recall))


#Resultado Memo
client = MongoClient('localhost', 27017)
db = client.NERLegales
collection = db.Entidades
result = collection.find({})
memoResults = []
for element in result:
	memoResults.append(element["Nombre"].lower())

#Calculo de precisión y exhaustividad
TP = 0
FP = 0
for element in memoResults:
	if element in goldStandard:
		TP = TP + 1
	else:
		FP = FP + 1
precision = (TP/(TP+FP))*100
FN = 0
for element in goldStandard:
	if element not in memoResults:
		FN = FN + 1
recall = (TP/(TP+FN))*100

print("Memo")
print("Precision:" + str(precision))
print("Recall: " + str(recall))
