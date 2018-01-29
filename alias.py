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
path_docx = "DOCX"
path_txt = path_docx.strip("/") + "_txt"
if not os.path.isdir(path_txt):
	os.makedirs(path_txt)

class Entidad:
	def __init__(self, entidad, alias):
		self.entidad = listaNombres
		self.alias = alias
		
def limpiarCadena(string):
	'''
	Recibe una cadena (generalmente un candidato), elimina comillas, comas y paréntesis.
	Devuelve una cadena
	'''
	#Tomamos una cadena (generalmente un candidato), y le quitamos basura.
	string = string.replace(u'“',"")
	string = string.replace(u'”',"")		
	string = string.replace(",","")
	string = string.replace("(","")
	string = string.replace(")","")
	string = string.replace('"',"")
	string = string.replace("'","")
	string = string.replace("en lo sucesivo","")
	return string

def checarArticulo(candidato):
	'''
	Recibe una cadena, y revisa si contiene un artículo. Si sí,
	devuelve el artículo y la palabra siguiente.
	'''
	listaCandidato = candidato.split()
	for elem in listaCandidato:
		if elem in ["la", "las", "lo", "los", "el"]:
			articulo = elem + " " + listaCandidato[listaCandidato.index(elem)+1]
			return articulo
			break;
	return ""

def Siglas(candidato,parrafo):
	'''
	Recibe un candidato (cadena) y un párrafo (cadena).
	A priori se sabe que el candidato son SIGLAS. 
	Se realiza una búsqueda hacia atrás en el párrafo, buscando las letras mayúsculas de las siglas.
	Una vez encontradas, se devuelve la entidad.
	'''
	entidad = []
	siglas = candidato.split()[0]
	indice = len(parrafo)-1 #última posición del párrafo
	for indice in range(indice,0,-1):
		if parrafo[indice] == siglas[-1]:
			siglas = siglas[:-1]
		if not siglas:
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(candidato.split()[0])
			break;
	return entidad	

def buscarArticulo(articulo,candidato,parrafo):
	'''
	Recibimos artículo y la palabra siguiente (producto de checarArticulo), un candidato, y su contexto.
	Buscamos artículo y la palabra siguiente en el párrafo para determinar la entidad nombrada.
	'''
	indice = 0
	entidad = []
	listaArticulo = articulo.split()
	listaCandidato = candidato.split()
	if articulo:
		if not listaArticulo[1].isupper():	#Si la palabra siguiente no son siglas
			listaParrafo = parrafo.split()
			for index, element in reversed(list(enumerate(listaParrafo))):
				indexMaximo = len(listaParrafo) - 1
				if index != indexMaximo:
					if limpiarCadena(element) == listaArticulo[0]:
						if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1]:
							indice = index
							break;
			if indice != 0:
				entidad.append(limpiarCadena(" ".join(listaParrafo[indice+1:]))) #indice + 1 para quitar el artículo
				candidato = candidato.replace(listaArticulo[0],"") #candidato es el alias, sin el artículo.
				entidad.append(candidato)
				return entidad
			#por lo tanto, vamos a buscar todo el candidato dentro del contexto, y donde lo encontremos, lo tomaremos 
			#como la entidad.
			else: #si indice = 0, significa que no se encontró el artículo seguido de la palabra.
				candidato = " ".join(listaCandidato[1:]) #cambiamos nuestro candidato, al puro alias, sin artículo.
				indice = parrafo.find(candidato)
				entidad.append(limpiarCadena(parrafo[-indice:]))
				entidad.append(candidato)
				return entidad
		else: #La 2da palabra sí son siglas.
			entidad = Siglas(listaArticulo[1],parrafo)
			return entidad

def regla1(candidato, parrafo):
	'''
	Recibe un candidato a entidad nombrada, y su contexto (párrafo).
	Devuelve la entidad nombrada
	
	Regla 1: Si dentro del paréntesis dice "en lo sucesivo" sin importar mayúsculas o minúsculas.
	
	Limpiamos el contenido del paréntesis y determinamos si hay un artículo.
	Si lo hay, buscamos en el contexto hacia atrás hasta que encontremos dicho artículo seguido de la
	primera palabra del candidato, y eso es la entidad nombrada.
	
	Si no hay artículo, y el candidato son siglas, entonces buscamos las letras mayúsculas
	en el contexto, y tomamos eso como la entidad.
	'''
	entidad = []
	candidato = limpiarCadena(candidato)
	articulo = checarArticulo(candidato)
	entidad = buscarArticulo(articulo,candidato,parrafo)
	if articulo == '' and len(candidato.split()) == 1 and candidato.split()[0].isupper(): #si no hubo artículo, la lista sólo mide 1, y son todas mayúsculas.
		entidad = Siglas(candidato,parrafo)
		return entidad
	print ("Entidad Regla 1")
	return entidad		

def regla2(candidato,parrafo):
	'''
	Recibe un candidato a entidad nombrada, y su contexto (párrafo).
	Devuelve la entidad nombrada
	
	Regla 2: Si dentro del paréntesis sólo hay una palabra. 
	
	Si son siglas, se buscan las letras mayúsculas en el contexto, y tomamos eso como la entidad.
	Si es una palabra, se busca hacia atrás la palabra, y lo que resta se toma como la entidad nombrada
	'''
	entidad = []
	candidato = limpiarCadena(candidato)
	if candidato.isupper():
		entidad = Siglas(candidato,parrafo)
		return entidad
	else:
		listaParrafo = parrafo.split()
		indice = 0
		for index, element in reversed(list(enumerate(listaParrafo))):
			if limpiarCadena(element) == candidato:
				indice = index
				break;
		if indice != 0:
			entidad.append(limpiarCadena(" ".join(listaParrafo[indice:])))
			entidad.append(candidato)
			print ("Entidad Regla 2")
			return entidad
		else:
			print ("Entidad Regla 2")
			return entidad

def Contexto(indiceInicial, textoPlano):
	'''
	Recibe un índice y un texto. 
	
	El índice corresponde al índice donde se ha detectado un candidato.
	Devuelve la cadena detrás del índice hasta el primer salto de línea.
	'''
	indiceFinal = indiceInicial
	while textoPlano[indiceFinal] != '\n':
		indiceFinal -= 1
	contexto = textoPlano[indiceFinal+1:indiceInicial] #Se suma 1 a indicFinal para no tomar el \n
	return contexto

'''
Flujo inicial del programa
'''
for fname in os.listdir(path_docx):
	fullpath = os.path.join(path_docx, fname)
	print ("Archivo: " + fullpath + "\n")
	textoPlano = docx2txt.process(fullpath)
	regexpParentesis = re.compile("\((.*?)\)")
	regexpComillas = re.compile('\"(.*?)\"')
	for element in regexpParentesis.finditer(textoPlano):
		parrafo = Contexto(element.start(),textoPlano) #element.start() tiene el index del 1er elemento donde hubo match
		entidad = regla1(element.group(), parrafo) #element.group() tiene el match en sí (el candidato)
		print ("Contexto: " + parrafo + "")
		print ("Candidato: " + element.group() + "")
		if entidad:
			print ("Entidad: " + entidad[0] + "")
			print ("Alias: " + entidad[1] + "\n")
		else:
			entidad = regla2(element.group(), parrafo)
			if entidad:
				print ("Entidad: " + entidad[0] + "")
				print ("Alias: " + entidad[1] + "\n")
			else:
				print ("Entidad: Vacía \n")
