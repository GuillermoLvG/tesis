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
#TO-DO: Usar la librería csv para escribir en el csv.
path_docx = "DOCX"
path_txt = path_docx.strip("/") + "_txt"
if not os.path.isdir(path_txt):
	os.makedirs(path_txt)

class Entidad:
	def __init__(self, entidad, alias):
		self.entidad = entidad
		self.alias = alias
		
def limpiarCadena(string):
	'''
	Recibe una cadena (generalmente un candidato), elimina comillas, comas y paréntesis.
	Devuelve una cadena
	'''
	string = string.replace(u'“',"")
	string = string.replace(u'”',"")		
	string = string.replace(",","")
	string = string.replace("(","")
	string = string.replace(")","")
	string = string.replace('"',"")
	string = string.replace("'","")
	string = string.replace("en lo sucesivo","")
	string = string.replace("en la sucesivo","")
	string = string.strip()
	return string

def limpiarParrafo(string):
	string = string.replace(" del "," de el ")
	return string
	
def obtenerArticulo(candidato):
	'''
	Recibe una cadena, y revisa si contiene un artículo. Si sí,
	devuelve el artículo y la palabra siguiente, si empieza con mayúscula.
	'''
	listaCandidato = candidato.split()
	for elem in listaCandidato:
		if elem in ["la", "las", "lo", "los", "el"]:
			if listaCandidato[listaCandidato.index(elem)+1][0].isupper():
				articulo = elem + " " + listaCandidato[listaCandidato.index(elem)+1]
				return articulo
				break;
	return ""

def buscarEnDiccionario(candidato):
	'''
	Recibe un alias ya limpio y devuelve una entidad con base en un diccionario, y el alias
	como una lista donde el primer elemento es la entidad y el segundo elemento el alias.
	
	1.- Abre el diccionario, y lo convierte a un diccionario donde la llave son los alias.
	2.- Se busca el alias (candidato) en el diccionario y se devuelve el value (entidad) como un string
	
	'''


def Siglas(candidato,parrafo):
	'''
	Recibe siglas (cadena), al que aquí se denomina "candidato" y un párrafo (cadena).
	A priori se sabe que el candidato son SIGLAS.
	
	Se realiza una búsqueda hacia atrás en el párrafo, buscando las letras mayúsculas de las siglas.
	Una vez encontradas, se devuelve la entidad.
	
	Si no se encontraron, se busca hacia atrás en el párrafo, buscando las letras minúsculas con las
	que empieza cada palabra. Una vez encontradas, se devuelve la entidad.
	
	Si no se encontró nada, se busca las siglas en mayúsculas pero sin importar el orden.
	'''
	entidad = []
	#Buscar mayúsculas
	siglas = candidato.split()[0]
	indice = len(parrafo)-1 #última posición del párrafo
	print("Siglas: " + siglas)
	for indice in range(indice,0,-1):
		if parrafo[indice] == siglas[-1]:
			siglas = siglas[:-1]
		if not siglas: #cuando terminé de buscar las siglas, devuelvo la entidad.
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(candidato.split()[0])
			print ("Busqué mayúsculas")
			return entidad
	#Buscar minúsculas
	siglas = candidato.split()[0].lower()
	indice = len(parrafo)-1
	for indice in range(indice,0,-1):
		if parrafo[indice] == siglas[-1]:#Aquí verifico que la minuscula sea inicio de palabra
			if parrafo[indice-1] == " ":
				siglas = siglas[:-1]
		if not siglas: 
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(candidato.split()[0])
			print ("Busqué minúsculas")
			return entidad
	#Buscar mayúsculas sin importar orden
	siglas = candidato.split()[0]
	indice = len(parrafo)-1
	for indice in range(indice,0,-1):
		if parrafo[indice].isupper() and parrafo[indice] in siglas: #Si la letra es mayúscula y está en "siglas"
			siglas = siglas.replace(parrafo[indice],"")
			print (siglas)
		if not siglas: 
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(candidato.split()[0])
			print ("Busqué mayúsculas sin importar el orden")
			return entidad
	#No encontró las siglas.
	print ("No encontré las siglas.")
	return entidad

def checarSiglas(candidato):
	'''
	Recibe una palabra (string)
	Si son siglas, devuelve las siglas. Si no, devuelve vacío.

	Las siglas que devuelve están limpias. Es decir, son 
	sólo letras mayúsculas.
	'''
	contMayus = 0
	contMinus = 0
	siglasLimpias = ""
	for letra in candidato:
		if letra.isupper():
			contMayus = contMayus + 1
			siglasLimpias = "" + siglasLimpias + "" + letra
		else:
			contMinus = contMinus + 1
	if contMayus >= contMinus:
		return siglasLimpias;
	else:
		siglasLimpias = ""
		return siglasLimpias

def buscarArticulo(articulo,candidato,parrafo):
	'''
	Recibimos artículo y la palabra siguiente (producto de checarArticulo), un candidato, y su contexto.
	Devolvemos artículo y la palabra siguiente en el párrafo para determinar la entidad nombrada.
	
	1.- Partimos el articulo en sus 2 partes. Artículo y palabra.
	2.- Partimos el candidato por espacios. El candidato es un candidato a Alias.
	3.- Recorremos el párrafo hacia atrás, Buscando si se presenta artículo + palabra
		y guardamos el índice de la ocurrencia.
	4.- Si no se encuentra, intentamos buscando con palabra en mayúscula, y si no, en minúscula.
	5.- Si no se encuentra tampoco, buscamos la pura palabra en minúscula.
	6.- De lo qu hayamos encontrado, tomamos del índice en adelante como entidad nombrada, omitiendo el artículo.
	7.- Tomamos el candidato como Alias, omitiendo el artículo.
	'''
	indice = 0
	entidad = []
	palabraSola = False
	listaArticulo = articulo.split()
	listaCandidato = candidato.split()
	if articulo:
		listaParrafo = parrafo.split()
		indexMaximo = len(listaParrafo) - 1
		encontreAlgo = False
		#Buscamos articulo + Palabra (primera letra de palabra en mayúscula, tal como viene la variable articulo)
		for index, element in reversed(list(enumerate(listaParrafo))):
			if index != indexMaximo:
				if limpiarCadena(element) == listaArticulo[0]:
					if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1]:
						indice = index
						print("Encontré articulo + Palabra")
						encontreAlgo = True
						break;
		#Buscamos articulo + PALABRA (la palabra en mayúscula)
		if not encontreAlgo:
			for index, element in reversed(list(enumerate(listaParrafo))):
				if index != indexMaximo:
					if limpiarCadena(element) == listaArticulo[0]:
						if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1].upper():
							indice = index
							print("Encontré articulo + PALABRA")
							encontreAlgo = True
							break;
		#Buscamos articulo + palabra (la palabra en minúscula)
		if not encontreAlgo:
			for index, element in reversed(list(enumerate(listaParrafo))):
				if index != indexMaximo:
					if limpiarCadena(element) == listaArticulo[0]:
						if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1].lower():
							indice = index
							print("Encontré articulo + palabra")
							encontreAlgo = True
							break;
		#Buscamos palabra (la palabra en minúscula)
		if not encontreAlgo:
			for index, element in reversed(list(enumerate(listaParrafo))):
				if index != indexMaximo:
					if limpiarCadena(element) == listaArticulo[1]:
						indice = index
						print (indice)
						palabraSola = True
						print("Encontré palabra tal como viene escrita")						
						encontreAlgo = True
						break;		#Buscamos palabra (la palabra en minúscula)
		if not encontreAlgo:
			for index, element in reversed(list(enumerate(listaParrafo))):
				if index != indexMaximo:
					if limpiarCadena(element) == listaArticulo[1].lower():
						indice = index
						palabraSola = True
						print("Encontré palabra en minúscula")						
						encontreAlgo = True
						break;
		#Encontramos algo
		if encontreAlgo:
			if not palabraSola:
				entidad.append(limpiarCadena(" ".join(listaParrafo[indice+1:]))) #indice + 1 para quitar el artículo
			else:
				entidad.append(limpiarCadena(" ".join(listaParrafo[indice:]))) #Quitamos el + 1, para no quitar la palabra sola.
			candidato = candidato.replace(listaArticulo[0],"") #candidato es el alias, sin el artículo.
			entidad.append(candidato)
			return entidad
		#No encontramos nada
		else: 
			print ("No encontré el artículo con la palabra, ni la palabra sola, ni nada.")
			return entidad

def regla1(candidato, parrafo):
	'''
	Recibe un candidato a entidad nombrada (str) , y su contexto (párrafo) (str).
	Devuelve la entidad nombrada (lista de 2 elementos str, el 1ro es la entidad y el 2do el alias)
	
	Regla 1: Si dentro del paréntesis hay un artículo 
	seguido de una palabra que empieza en mayúsculas, o seguido de siglas.
	y el contenido del paréntesis es de menos de 10 palabras.
	
	Procedimiento:
	1.- Limpiamos el contenido del paréntesis  (func. limpiarCadena)
	2.- Verificamos si el contenido del paréntesis tiene menos de 10 palabras.
	3.- Determinamos si hay un artículo seguido de una palabra que empieza en mayúscula, o seguido de siglas (func. obtenerArticulo)
	4.- Vemos si lo que le sigue al artículo es una palabra, o son siglas. (func. checarSiglas)
	5.- Si son siglas, buscamos hacia atrás las letras mayúsculas
		letra por letra, y cuando encuentra todas, regresa la entidad (func. Siglas)
	6.- Si es una palabra, buscamos en el contexto hacia atrás hasta que encontremos dicho artículo 
		seguido de la primera palabra del candidato, y eso es la entidad nombrada. (func.buscarArticulo)
	7.- Si no se encontró la paĺabra con el artículo, se busca sólo la palabra, sin el artículo.
	'''
	entidad = []
	candidato = limpiarCadena(candidato)
	print(candidato)
	if len(candidato.split()) > 10: #Checamos que sea menor de 10 palabras
		return entidad
	articulo = obtenerArticulo(candidato)
	if articulo:
		print ("Tiene Artículo")
		print ("Articulo + palabra: " + articulo)
		if checarSiglas(articulo.split()[1]): #Checamos si son siglas. 
			print("Son Siglas")
			print(articulo.split()[1])
			entidad = Siglas(articulo.split()[1],parrafo)
		else:
			print("Busca Artículo")
			entidad = buscarArticulo(articulo,candidato,parrafo)
	return entidad

def regla2(candidato,parrafo):
	'''
	Recibe un candidato a entidad nombrada (str), y su contexto (párrafo) (str).
	Devuelve la entidad nombrada (lista de 2 elementos str, el 1ro es la entidad y el 2do el alias)
	
	Regla 2: Si dentro del paréntesis sólo hay una palabra, 
	o la primer palabra está en mayúscula.
	
	Procedimiento:
	1.- Limpiamos el contenido del paréntesis. (func. limpiarCadena)
	2.- Si son siglas, entonces buscamos cada letra mayúscula de las siglas en 
		el contexto, y una vez encontradas, obtenemos la entidad. (func. Siglas)
	3.- Si son varias palabras en el paréntesis, tomamos sólo la primera si empieza en mayúscula.
	3.- Si es una palabra, se busca hacia atrás en el párrafo, y cuando se encuentra, se toma desde
		esa posición, hasta el fin del párrafo como entidad nombrada.
	4.- Si son muchas palabras, y la primera está en mayúscula, se toma la primera palabra como si
		fuese la única., y se repite el paso 3.
	'''
	entidad = []
	indice = 0
	candidato = limpiarCadena(candidato)
	if checarSiglas(candidato):
		print("Son Siglas")
		entidad = Siglas(candidato,parrafo)
		return entidad
	else:
		print ("Es una palabra")
		palabra = candidato
		if len(candidato.split()) != 1 and candidato.split()[0][0].isupper(): #si son varias palabras, y la primer palabra empieza en mayúsculas.
			palabra = candidato.split()[0]
		listaParrafo = parrafo.split()
		print ("La palabra es: " + palabra)
		for index, element in reversed(list(enumerate(listaParrafo))):
			if limpiarCadena(element) == palabra:
				indice = index
				break;
		if indice != 0:
			entidad.append(limpiarCadena(" ".join(listaParrafo[indice:])))
			entidad.append(candidato)
			return entidad
		else:
			return entidad		

def regla3(candidato, parrafo):
	'''
	Recibe un candidato a entidad nombrada (str) , y su contexto (párrafo) (str).
	Devuelve la entidad nombrada (lista de 2 elementos str, el 1ro es la entidad y el 2do el alias)
	
	Regla 3: Si dentro del paréntesis está presente la palabra "siglas"
	
	Procedimiento:
	1.- Limpiamos el contenido del paréntesis (func. limpiarCadena)
	2.- Verificar que el candidato contenga la palabra "siglas"
	3.- Si sí, para cada palabra del candidato, buscar la palabra que sean siglas.
	4.- Si son siglas, buscamos hacia atrás las letras mayúsculas
		letra por letra, y cuando encuentra todas, regresa la entidad (func. Siglas)
	'''
	entidad = []
	candidato = limpiarCadena(candidato)
	if "siglas" not in candidato:
		return entidad
	listaPalabras = candidato.split()
	for palabra in listaPalabras:
		if checarSiglas(palabra):
			entidad = Siglas(palabra,parrafo)
			return entidad
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
os.remove("tablas/resultado.csv")
for fname in os.listdir(path_docx):
	fullpath = os.path.join(path_docx, fname)
	print ("Archivo: " + fullpath + "\n")
	textoPlano = docx2txt.process(fullpath)
	regexpParentesis = re.compile("\((.*?)\)")
	regexpComillas = re.compile('\"(.*?)\"')
	for element in regexpParentesis.finditer(textoPlano):
		indiceOcurrencia = element.start() #element.start() tiene el index del 1er elemento donde hubo match
		candidato = element.group() #element.group() tiene el match en sí (el candidato)
		parrafo = Contexto(indiceOcurrencia,textoPlano)
		parrafo = limpiarParrafo(parrafo)
		print ("Regla 1")
		entidad = regla1(candidato, parrafo)
		print ("Contexto: " + parrafo + "")
		print ("Candidato: " + element.group() + "")
		if entidad:
			entidad = Entidad(entidad[0],entidad[1])
			print ("Entidad: " + entidad.entidad + "")
			print ("Alias: " + entidad.alias + "\n")
			with open('tablas/resultado.csv','a+') as salida:
				salida.write(entidad.alias.strip() + "," + entidad.entidad.strip() + "," + candidato.replace(",","").strip() + "," + parrafo.replace(",","").strip() + ",Regla 1," + fname + "\n")
		else:
			print ("Regla 2")
			entidad = regla2(candidato, parrafo)
			if entidad:
				entidad = Entidad(entidad[0],entidad[1])
				print ("Entidad: " + entidad.entidad + "")
				print ("Alias: " + entidad.alias + "\n")
				with open('tablas/resultado.csv','a+') as salida:
					salida.write(entidad.alias.strip() + "," + entidad.entidad.strip() + "," + candidato.replace(",","").strip() + "," + parrafo.replace(",","").strip() + ",Regla 2," + fname + "\n")
			else:
				print ("Regla 3")
				entidad = regla3(candidato,parrafo)
				if entidad:
					entidad = Entidad(entidad[0],entidad[1])
					print ("Entidad: " + entidad.entidad + "")
					print ("Alias: " + entidad.alias + "\n")
					with open('tablas/resultado.csv','a+') as salida:
						salida.write(entidad.alias.strip() + "," + entidad.entidad.strip() + "," + candidato.replace(",","").strip() + "," + parrafo.replace(",","").strip() + ",Regla 3," + fname + "\n")
				else:
					with open('tablas/resultado.csv','a+') as salida:
						salida.write("Vacía, Vacía ," + candidato.replace(",","").strip() + "," + parrafo.replace(",","").strip() + ",Regla 3," + fname + "\n")
					print ("Entidad: Vacía \n")
