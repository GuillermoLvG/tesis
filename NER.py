# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
#------------------------------------------------------
# No recibe argumentos.
# Busca los archivos en DOCX_txt, y a cada uno le saca una lista de alias, los cuales
# asocia a una entidad.
# Obtiene también entidades sin alias.
# Todo se guarda en una base de datos en MongoDB
#------------------------------------------------------
import docx2txt
import os
import sys
import re
import csv
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
client.drop_database('NERLegales')
db = client.NERLegales
collection = db.Entidades
path_docx = "Evaluacion/CorpusEval/Archivo"

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
	string = string.replace("en delante","")
	string = string.replace("en adelante","")
	string = string.replace("en conjunto","")
	string = string.strip()
	return string
def limpiarParrafo(string):
	string = string.replace(" del "," de el ")
	return string
def limpiarCadenaNER(string):
	'''
	Recibe una cadena, devuelve una cadena

	Reemplaza lo que sea necesario en la cadena.
	'''
	string = string.strip()
	string = string.replace(",","")
	string = string.replace("CC. ","")
	string = string.replace("C. ","")
	string = string.replace("CC. ","")
	string = string.replace("Mtro. ","")
	string = string.replace("Mtra. ","")
	string = string.replace("Sra. ","")
	string = string.replace("Sr. ","")
	string = string.replace("Lic. ","")
	string = string.replace("Dr. ","")
	string = string.replace("Dra. ","")
	string = string.replace("Pdte. ","")
	string = string.replace("Ingeniero ","")
	string = string.replace("Comisionado ","")
	string = string.replace("Comisionados ","")
	string = string.replace("Comisionada ","")
	string = string.replace("(","")
	string = string.replace(")","")
	return string
def obtenerContexto(indiceInicial, textoPlano):
	'''
	Recibe un índice y un texto.

	El índice corresponde al índice donde se ha detectado un candidato.
	Devuelve la cadena detrás del índice hasta el primer salto de línea.
	'''
	indiceFinal = indiceInicial
	while textoPlano[indiceFinal] != '\n' and indiceFinal != 0:
		indiceFinal -= 1
	if indiceFinal == 0:
		contexto = textoPlano[indiceFinal:indiceInicial]
	else:
		contexto = textoPlano[indiceFinal+1:indiceInicial] #Se suma 1 a indicFinal para no tomar el \n
	return limpiarParrafo(contexto)
def obtenerArticulo(candidato):
	'''
	Recibe una cadena, y revisa si contiene un artículo. Si sí,
	devuelve el artículo y la palabra siguiente, si empieza con mayúscula.
	'''
	listaCandidato = candidato.split()
	for elem in listaCandidato:
		if elem in ["la", "las", "lo", "los", "el"] and len(listaCandidato) > 1:
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
	entidad = []
	with open('Diccionarios/Diccionario.csv', mode='r') as infile:
		reader = csv.reader(infile)
		diccionario = {rows[0].lower():rows[1] for rows in reader}
		diccionarioInverso = {v.lower(): k for k, v in diccionario.items()}
	print ("Buscando '" + candidato.lower() + "' en el diccionario")
	if candidato.lower() in diccionario:
		print ("Se encontró en diccionario original")
		entidad.append(diccionario[candidato.lower()])
		entidad.append(candidato)
	elif candidato.lower() in diccionarioInverso:
		print ("Se encontró en diccionario invertido")
		entidad.append(candidato)
		entidad.append(diccionarioInverso[candidato.lower()])
	return entidad
def buscarArticulo(articulo,candidato,parrafo):
	'''
	Recibimos artículo y la palabra siguiente (producto de checarArticulo), un candidato, y su contexto.
	Devolvemos artículo y la palabra siguiente en el párrafo para determinar la entidad nombrada.

	1.- Partimos el articulo en sus 2 partes. Artículo y palabra.
	2.- Partimos el candidato por espacios. El candidato es un candidato a Alias.
	3.- Vemos si el artículo es singular o plural. Si es singular entonces recorremos el párrafo 3
		hacia atrás, Buscando si se presenta artículo + palabra y guardamos el índice de la ocurrencia.
	5.- Si no se encuentra, intentamos buscando con palabra en mayúscula, y si no, en minúscula.
	6.- Si no se encuentra tampoco, buscamos la pura palabra en minúscula.
	7.- De lo que hayamos encontrado, tomamos del índice en adelante como entidad nombrada, omitiendo el artículo.
	8.- Tomamos el candidato como Alias, omitiendo el artículo.
	9.- Si el artículo fue plural, entonces con una expresión regular encontramos todos los matches de entidades en el contexto
		las concatenamos y las metemos como string en "entidad".
	'''
	indice = 0
	entidad = []
	palabraSola = False
	listaArticulo = articulo.split()
	listaCandidato = candidato.split()
	listaParrafo = parrafo.split()
	indexMaximo = len(listaParrafo) - 1
	encontreAlgo = False
	#Buscamos articulo + Palabra (primera letra de palabra en mayúscula, tal como viene la variable articulo)
	for index, element in reversed(list(enumerate(listaParrafo))):
		if index != indexMaximo:
			if limpiarCadena(element) == listaArticulo[0]:
				#Buscamos articulo + Palabra (primera letra de palabra en mayúscula, tal como viene la variable articulo)
				if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1]:
					indice = index
					print("Encontré articulo + Palabra")
					encontreAlgo = True
					break;
				#Buscamos articulo + PALABRA (la palabra en mayúscula)
				if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1].upper():
					indice = index
					print("Encontré articulo + PALABRA")
					encontreAlgo = True
					break;
				#Buscamos articulo + palabra (la palabra en minúscula)
				if limpiarCadena(listaParrafo[index+1]) == listaArticulo[1].lower():
					indice = index
					print("Encontré articulo + palabra")
					encontreAlgo = True
					break;
	#Buscamos palabra sola, sin artículo,
	if not encontreAlgo:
		for index, element in reversed(list(enumerate(listaParrafo))):
			if index != indexMaximo:
				#Busco la palabra en minúscula
				if limpiarCadena(element) == listaArticulo[1].lower():
					indice = index
					palabraSola = True
					print("Encontré palabra en minúscula")
					encontreAlgo = True
					break;
				#Buscamos palabra (la palabra tal como viene escrita)
				if limpiarCadena(element) == listaArticulo[1]:
					indice = index
					palabraSola = True
					print("Encontré palabra tal como viene escrita")
					encontreAlgo = True
					break;
	#Buscamos, si el artículo es plural, una lista de entidades. más de dos.
	if not encontreAlgo:
		if listaArticulo[0] in ["los", "las"]:
			print ("Artículo plural")
			expresion = r"\b([A-Z][a-záéíóú]+ ?)+(((la|el|los|las|un|una|uno|unas|unos|y|con|de|del) )*([A-Z][a-záéíóú]+ ?)+)*((, )?| )(S.A. de C.V.)"
			regex = re.compile(expresion)
			matches = regex.finditer(parrafo)
			Entidades = ""
			if len(list(matches)) >= 2:
				print ("Hay más de dos entidades encontradas")
				for match in regex.finditer(parrafo):
					Entidades = Entidades + ", " + match.group(0)
				Entidades = Entidades[2:] #Para quitar la coma del inicio de la enumeración.
				entidad.append(Entidades)
				candidato = candidato.replace(listaArticulo[0] + " ", "")
				entidad.append(candidato)
				return entidad
	#Encontramos algo
	if encontreAlgo:
		if not palabraSola:
			entidad.append(limpiarCadena(" ".join(listaParrafo[indice+1:]))) #indice + 1 para quitar el artículo
		else:
			entidad.append(limpiarCadena(" ".join(listaParrafo[indice:]))) #Quitamos el + 1, para no quitar la palabra sola.
		candidato = candidato.replace(listaArticulo[0] + " ","") #candidato es el alias, sin el artículo.
		entidad.append(candidato)
		return entidad
	#No encontramos nada
	else:
		print ("No encontré el artículo con la palabra, ni la palabra sola, ni nada.")
		return entidad
def buscarConjuncion(candidato):
	'''
	recibe un candidato, busca una conjunción, y devuelve lista de N candidatos.
	La lista son las entidades separadas.
	'''
	print("Entren con "+ candidato)
	if len(candidato.split()) < 15:
		if " y la " in candidato:
			candidatoConjuncion = candidato.split(" y la ")
			if len(candidatoConjuncion[1].split()) < 3 :
				return candidato
			print ("Hubo conjunción <y la> en " + candidato)
			return candidatoConjuncion
		if " y el " in candidato:
			candidatoConjuncion = candidato.split(" y el ")
			if len(candidatoConjuncion[1].split()) < 3:
				return candidato
			print ("Hubo conjunción <y el> en " + candidato)
			return candidatoConjuncion
		if " de la " in candidato:
			candidatoConjuncion = candidato.split(" de la ")
			if len(candidatoConjuncion[1].split()) < 3:
				return candidato
			print ("Hubo conjunción <de la> en " + candidato)
			return candidatoConjuncion
		if " y " in candidato:
			candidatoConjuncion = candidato.split(" y ")
			if len(candidatoConjuncion[1].split()) < 3 and len(candidatoConjuncion[0].split()) > 2:
				return candidato
			print ("Hubo conjunción <y> en " + candidato)
			return candidatoConjuncion
	print ("No hubo conjunción en " + candidato)
	return candidato
def buscarEntidades(texto,fname):
	'''
	Recibe una cadena y el nombre del archivo.

	1.- Se busca una expresión regular que devuelve palabras que empiezan en mayúscula, separadas por (la|el|los|las|un|una|uno|unas|unos|y|con|de|del|a), y seguidas
		por más palabras en mayúscula, que pueden estar seguidas o no de (S.A. de C.V.|S. de R.L. de C.V.).
	2.- De lo que devuelve la expresión regular, se buscan conjunciones para separar las entidades encontradas por el "y"
	3.- Cada match de la expresión es un candidato, al cual aplicamos una serie de reglas en ReglasNER.
	4.- Si se cumplen las reglas, se agrega el match como entidad.
	4.- Se busca una expresión regular que devuelve la palabra que sige de Oficio, Expediente u Acuerdo, si contiene diagonales y guiones.
	5.- Se agrega lo encontrado como entidad.
	6.- Se busca el diccionario de municipios
	'''
	resultados = []
	#Expresión 1
	expresion = r"\b(((CC.|C.|Mtro.|Mtra.|Sra.|Sr.|Lic.|Dr.|Dra.|Pdte.) )?([A-Z][a-záéíóú]+ ?)+(((la|el|los|las|un|una|uno|unas|unos|y|con|de|del|a) )*([A-Z][a-záéíóú]+ ?)+)*((, )?| )?(S.A. de C.V.|S. de R.L. de C.V.|S.A.B. de C.V.|S.A.)?)"
	regex = re.compile(expresion)
	matches = regex.finditer(texto)
	for match in matches:
		candidatos = buscarConjuncion(limpiarCadenaNER(match.group()))
		if type(candidatos) != list:
			candidatos = [candidatos]
		for candidato in candidatos:
			print ("Candidato: " + candidato)
			candidato = ReglasNER(candidato,fname,texto)
			if candidato:
				indiceOcurrencia = match.start()
				Regla = "Expresión Regular"
				categoria = clasificador(candidato)
				resultado = {"Nombre": candidato, "Clase": categoria, "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } }
				resultados.append(resultado)
	#Expresión 2
	expresion = r"((o|O)ficio|(e|E)xpediente|(a|A)cuerdo|(O|o)pinión) (.*?número )?([A-Z]|[0-9]|,|\.|;|:|\\)*(/|-)([A-Z]|[0-9]|;|:|\\|/|-)*"
	regex = re.compile(expresion)
	matches = regex.finditer(texto)
	for match in matches:
		entidad = match.group()
		indiceOcurrencia = match.start()
		Regla = "Expresión Regular Documento"
		print("Oficio, Expediente, Acuerdo, Opinión: " + entidad)
		resultado = {"Nombre": entidad,  "Clase": "Documento", "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } }
		resultados.append(resultado)
	#Expresión 3
	expresion = r"([0-9]*,? )*((A|a)rtículos?|(F|f)racci(ó|o)n(es)?|(I|i)ncisos?|(P|p)árrafos?)( ?\S){0,100}? (del |de la )(abrogada )?([A-Z][a-záéíóú]+ ?)+(((la|el|los|las|un|una|uno|unas|unos|y|con|de|del|a) )*([A-Z][a-záéíóú]+ ?)+)*"
	regex = re.compile(expresion)
	matches = regex.finditer(texto)
	for match in matches:
		entidad = limpiarCadenaNER(match.group())
		indiceOcurrencia = match.start()
		Regla = "Expresión Regular Ley"
		print("Ley: " + entidad)
		resultado = {"Nombre": entidad,  "Clase": "Ley", "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } }
		resultados.append(resultado)
	return resultados
def diccionarioMunicipios(texto,fname):
	with open("Diccionarios/listaMunicipiosEstados.txt") as municipios:
		listaMunicipios = municipios.readlines()
	for municipio in listaMunicipios:
		municipio = municipio.strip()
		indiceOcurrencia = texto.find(municipio)
		print(municipio)
		regex = re.compile(r"((E|e)stado|(M|m)unicipio)( de )?"+municipio+r".*?")
		if indiceOcurrencia != -1:
			print (municipio)
			if collection.find({"Archivos.Nombre":fname.replace(".docx",""), "Nombre":{'$regex':regex}}).count() != 0:
				print ("Está en entidades")
			else:
				print("No está en entidades")
				entidad = municipio
				Regla = "Diccionario Municipios"
				print("Municipio: " + entidad)
				resultado = {"Nombre": entidad, "Clase": "Lugar", "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": "", "Regla": Regla } }
				insertarEnBD(resultado)
def buscarAliasEnBD(candidato,fname):
	'''
	Busca los alias en un archivo, y devuelve True si se encontró, y False si no.
	'''
	buscarAlias = collection.find({"Archivos.Nombre":fname.replace(".docx",""), "Archivos.Alias":candidato})
	for element in buscarAlias:
		if element["Archivos"]["Alias"]:
			return True
	return False
def inicioDePalabra(parrafo,indice):
	'''
	recibe un índice y un párrafo.
	Devuelve True si el índice corresponde a una letra que es inicio de una palabra
	y False si es no lo es.
	'''
	if indice != 0:
		if parrafo[indice-1] == " ":
			return True
		else:
			return False
	else:
		return True
def resolverSiglas(candidato,parrafo,siglasOriginales):
	'''
	Recibe siglas (cadena), al que aquí se denomina "candidato" y un párrafo (cadena).
	A priori se sabe que el candidato son SIGLAS.
	Devuelve la entidad y el alias.

	1.- Se busca hacia atrás en el párrafo, buscando las letras mayúsculas de las siglas en orden,
		y se devuelve la entidad y el alias. Se verifica siempre que la letra mayúscula sea un inicio
		de palabra (func. inicioDePalabra)
	2.- Se busca hacia atrás en el párrafo, buscando las letras minúsculas de las siglas en orden,
		y se devuelve la entidad y el alias. Se verifica que la minúscula sea inicio de palabra (func. inicioDePalabra)
	3.- Se busca hacia atrás en el párrafo las letras mayúsculas de las siglas sin importar el orden.
		Se devuelve la entidad y el alias. Se verifica siempre que la mayúscula sea inicio de
		palabra (func. inicioDePalabra)
	'''
	entidad = []
	#Buscar mayúsculas
	siglas = candidato.split()[0]
	indice = len(parrafo)-1 #última posición del párrafo
	print("Siglas: " + siglas)
	print("Buscando mayúsculas en orden")
	for indice in range(indice,0,-1):
		if parrafo[indice] == siglas[-1] and inicioDePalabra(parrafo,indice):#Si la letra es la sigla, y es inicio de palabra
			siglas = siglas[:-1]
			print(siglas)
		if not siglas: #cuando terminé de buscar las siglas, devuelvo la entidad.
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(siglasOriginales)
			print ("Encontré mayúsculas en orden")
			return entidad
	#Buscar minúsculas
	siglas = candidato.split()[0].lower()
	indice = len(parrafo)-1
	print("Buscando minúsculas en orden")
	for indice in range(indice,0,-1):
		if parrafo[indice] == siglas[-1] and inicioDePalabra(parrafo,indice): #Si la letra es la sigla, y es inicio de palabra
			siglas = siglas[:-1]
			print(siglas)
		if not siglas:
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(siglasOriginales)
			print ("Encontré minúsculas en orden")
			return entidad
	#Buscar mayúsculas sin importar orden
	siglas = candidato.split()[0]
	indice = len(parrafo)-1
	print("Buscando mayúsculas sin importar el orden")
	for indice in range(indice,0,-1):
		if parrafo[indice].isupper() and inicioDePalabra(parrafo,indice) and parrafo[indice] in siglas: #Si la letra es mayúscula, es inicio de palabra y está en "siglas"
			siglas = siglas.replace(parrafo[indice],"",1)
			print (siglas)
		if not siglas:
			entidad.append(limpiarCadena(parrafo[indice:len(parrafo)-1]))
			entidad.append(siglasOriginales)
			print ("Encontré mayúsculas sin importar el orden")
			return entidad
	#Obtener con una expresión regular las posibles entidads con mayúscula seguidas, separadas con artículos.
	siglas = candidato.split()[0]
	instancia = ""
	print("Buscando posibles entidades con Mayúsculas: ")
	expresion = r"\b([A-Z][a-záéíóú]+ ?)+(((la|el|los|las|un|una|uno|unas|unos|y|con|de|del) )*([A-Z][a-záéíóú]+ ?)+)*\b"
	regex = re.compile(expresion)
	for match in regex.finditer(parrafo):
		if len(match.group(0).split()) > 3:
			print("Posible entidad: " + match.group(0))
			instancia = match.group(0)
	if instancia:
		print("Se determinó a " + instancia + " como entidad")
		entidad.append(limpiarCadena(instancia))
		entidad.append(siglasOriginales)
		return entidad

	#No encontró las siglas.
	print ("No encontré las siglas.")
	return entidad
def reglasSiglas(candidato):
	'''
	Recibe una palabra (string)
	Si son siglas, devuelve las siglas. Si no, devuelve vacío.

	Las siglas que devuelve están limpias. Es decir, son
	sólo letras mayúsculas, Y une ciertos patrones comunes en siglas
	como "NA" por "N" (Nacional), "DI" por "D" (Dinámica).
	'''
	contMayus = 0
	contMinus = 0
	siglasLimpias = ""
	for letra in candidato:
		if letra.isupper():
			contMayus = contMayus + 1
			siglasLimpias = "" + siglasLimpias + "" + letra
		elif letra.isdigit():
			siglasLimpias = "" + siglasLimpias + "" + letra
		else:
			contMinus = contMinus + 1
	siglasLimpias = siglasLimpias.replace("NA","N")
	siglasLimpias = siglasLimpias.replace("DI","D")
	siglasLimpias = siglasLimpias.replace("TV","T")
	siglasLimpias = siglasLimpias.replace("CO","C")
	siglasLimpias = siglasLimpias.replace("FE","F")
	siglasLimpias = siglasLimpias.replace("TEL","T")
	siglasLimpias = siglasLimpias.replace("MEX","M")
	if contMayus >= contMinus:
		return siglasLimpias;
	else:
		siglasLimpias = ""
		return siglasLimpias
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
	4.- Vemos si lo que le sigue al artículo es una palabra, o son siglas. (func. reglasSiglas)
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
		siglas = reglasSiglas(articulo.split()[1]) #Checamos si son siglas y las obtenemos límpias.
		if siglas:
			print("Son Siglas")
			entidad = resolverSiglas(siglas,parrafo,articulo.split()[1])
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
	2.- Checamos si la palabra son siglas.
	3.- Si el candidato es un número, devolvemos entidad vacía.
	4.- Si son siglas, Se tratan como tal (func. Siglas)
	5.- Si son varias palabras en el paréntesis, tomamos sólo la primera si empieza en mayúscula.
	6.- Se busca la palabra hacia atrás en el párrafo, y cuando se encuentra, se toma desde
		esa posición, hasta el fin del párrafo como entidad nombrada.
	7.- Si no se encuentra, se utiliza wordnet para encontrar un grado de similitud entre la palabra,
		y las palabras anteriores. Se tiene un valor mínimo de similitud, y se toma como entidad desde
		la palabra con mayor similitud.
	'''
	entidad = []
	indice = 0
	encontreAlgo = False
	candidato = limpiarCadena(candidato)
	siglas = reglasSiglas(candidato)
	if candidato.isdigit():
		return entidad
	if siglas:
		entidad = resolverSiglas(siglas,parrafo,candidato)
		if entidad:
			print ("Fueron Siglas")
			return entidad
	print ("El paréntesis contiene palabra(s)")
	palabra = candidato
	if len(candidato.split()) != 1 and candidato.split()[0][0].isupper(): #si son varias palabras, y la primer palabra empieza en mayúsculas.
		print ("Son varias palabras, tomamos la primera por empezar en mayúscula")
		palabra = candidato.split()[0]
	listaParrafo = parrafo.split()
	print ("La palabra es: " + palabra)
	#Se busca la palabra tal cual hacia atrás en el documento.
	for index, element in reversed(list(enumerate(listaParrafo))):
		if limpiarCadena(element) == palabra:
			indice = index
			encontreAlgo = True
			break;
	if encontreAlgo:
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
		siglas = reglasSiglas(palabra)
		if siglas:
			entidad = resolverSiglas(siglas,parrafo,palabra)
			return entidad
	return entidad
def regla4(candidato):
	'''
	Recibe un candidato a entidad nombrada (str).
	Devuelve la entidad nombrada (lista de 2 elementos str, el 1ro es la entidad y el 2do el alias)

	Regla 4: Revisa si el candidato existe en una lista de entidades (diccionario).

	1.- Se limpia el candidato (func. limpiarCadena)
	2.- Se busca en el diccionario (func. buscarEnDiccionario)
	3.- Se devuelve la entidad y el alias.
	'''
	entidad = []
	candidato = limpiarCadena(candidato)
	entidad = buscarEnDiccionario(candidato)
	return entidad
def ReglasNER(candidato,fname,texto):
	'''
	Entra un candidato, aplica una serie de reglas, y decide si es una entidad o no. Si devuelve algo, entonces es entidad. Si devuelve vacío
	entonces no es.
	1.- Si sólo tiene una palabra, no es entidad
	2.- Si empieza con artículo, no es entidad
	3.- Si la entidad es un alias que ya encontramos anteriormente, no es entidad
	'''
	#Regla 1
	palabrasCandidato = candidato.split()
	if len(palabrasCandidato) < 3:
		print("Tiene menos de tres palabras")
		print("No es entidad \n")
		return ""
	#Regla 2
	if palabrasCandidato[0].lower() in ["la", "las", "lo", "los", "el", "del"]:
		print("La primer palabra es un artículo")
		print("No es entidad \n")
		return ""
	#Regla 3
	if buscarAliasEnBD(candidato,fname):
		print("Es un alias")
		print("No es entidad\n")
		return ""
	print("Si es entidad")
	print("Entidad: " + candidato + "\n")
	return candidato
def clasificador(entidad):
	'''
	Recibe una entidad (cadena) y arroja el tipo de entidad que es (cadena), utilizando ciertas reglas
	para cada clase: Persona, Organización, Título, Documentos, Leyes, Lugares
	'''
	palabrasEntidad = entidad.split()
	for palabra in palabrasEntidad:
		if palabra.lower() in ["dr.","mtro.","mtra.","lic.","presidente","c.","cc.","","comisionado","comisionada","coordinador","coordinadora","defensor","defensora","delegado","delegada","director","directora","responsable","secretario","secretaria","subsecretaria","subsecretario","titular"]:
			return "Persona"
		if palabra.lower() in ["ley","artículo","párrafo","sección"]:
			return "Ley"
		if palabra.lower() in ["banco","instituto","organización","s.a.","c.v.","dirección","administración","administradora","censo","comisión","competencia","consejo","consorcio","coordinación","departamento","disposición","ejecutivo","ejecutoría","gobierno","grupo","junta","juzgado","oficialía","organismo","pleno","sala","secretaría","sistema","subsecretaría","tribunal","tribunales","unidad","unidades","universidad",]:
			return "Organización"
		if palabra.lower() in ["acuerdo","expediente","constitución","acta","resolución","oficio","anexo","documento","concesión","constancia","contrato","código","decreto","derechos","diario","escrito","escritura","estatuto","formato","lineamiento","lineamientos","lista","manual","otorgamiento","presupuesto","prórroga","publicación","registro","reglamento","reglas","requerimiento","resolutivo","solicitud","solicitudes","opinión"]:
			return "Documento"
		if palabra.lower() in ["municio","estado","colonia","calle","delegación","oficina"]:
			return "Lugar"
	return "Otro"
def filtroAlias(candidatoAlias):
	if " " not in candidatoAlias and len(candidatoAlias) == 1:
		return False
	if candidatoAlias == "...":
		return False
	if "en los sucesivo" in candidatoAlias:
		return False
	return True
def aplicarReglasAlias(candidato,parrafo,fname,indiceOcurrencia):
	'''
	Aplica las reglas de forma secuencial.

	Devuelve un diccionario con los datos para ingresar en la base de datos.

	{
	Nombre: texto,
	Archivos: { Nombre del archivo: {indiceOcurrencia: numero, Alias: texto, Regla: texto } }
	Clase: texto
	}
	Las clases pueden ser Persona, Organización, Documentos, Leyes, Lugares, Otro
	'''
	try:
	    os.remove("tablas/resultado.csv")
	except OSError:
	    pass
	print ("Contexto: " + parrafo)
	print ("Candidato: " + candidato)
	Regla = ""
	entidad = ""
	resultadoEntidad = ""
	resultado = dict()
	entidad = regla1(candidato,parrafo)
	if entidad and not Regla:
		Regla = "Regla 1"
		resultadoEntidad = entidad
		categoria = clasificador(resultadoEntidad[0])
	entidad = regla2(candidato, parrafo)
	if entidad and not Regla:
		Regla = "Regla 2"
		resultadoEntidad = entidad
		categoria = clasificador(resultadoEntidad[0])
	entidad = regla3(candidato,parrafo)
	if entidad and not Regla:
		Regla = "Regla 3"
		resultadoEntidad = entidad
		categoria = clasificador(resultadoEntidad[0])
	entidad = regla4(candidato)
	if entidad and not Regla:
		Regla = "Regla 4"
		resultadoEntidad = entidad
		categoria = clasificador(resultadoEntidad[0])
	if resultadoEntidad:
		if filtroAlias(resultadoEntidad[1]):
			print (Regla)
			print ("Entidad: " + resultadoEntidad[0] + "")
			print ("Alias: " + resultadoEntidad[1] + "\n")
			with open('tablas/resultado.csv','a+') as salida:
				salida.write(resultadoEntidad[1].strip() + "," + resultadoEntidad[0].strip() + "," + candidato.replace(",","").strip() + "," + parrafo.replace(",","").strip() + "," + Regla + "," + fname + "\n")
				resultado = {"Nombre": resultadoEntidad[0], "Clase": categoria, "Archivos": {"Nombre":fname.replace(".docx",""), "indiceOcurrencia": indiceOcurrencia, "Alias": resultadoEntidad[1], "Regla": Regla} }
				return resultado
	return resultado
def insertarEnBD(resultado):
	'''
	Recibe un registro para insertar en la base de datos, y lo inserta.

	Si el registro es de una entidad que ya existe, se verifica el archivo donde ocurre, y si ya existe una ocurrencia
	anterior en ese archivo, entonces se agrega el nuevo índice de ocurrencia.
	Si la entidad ya existe, pero ocurre en un archivo nuevo, entonces se agrega el archivo nuevo donde ocurre.
	Si la entidad no existe, se agrega el registro tal cual.
	'''
	listaArchivos = []
	archivosEnBD = []
	indicesEnBD = []
	indiceNuevo = False
	entidadEnBD = collection.find_one({"Nombre": resultado["Nombre"]})
	if entidadEnBD:
		#Se tiene que convertir en lista, pues cuando el registro entra por primera vez, no es una lista. Sucede en "Archivos" y en "indiceOcurrencia"
		if type(entidadEnBD["Archivos"]) != list:
			archivosEnBD = [entidadEnBD["Archivos"]]
		else:
			archivosEnBD = entidadEnBD["Archivos"]
		for elemento in archivosEnBD:
			agregarElemento = elemento
			if agregarElemento["Nombre"] == resultado["Archivos"]["Nombre"]:
				if type(agregarElemento["indiceOcurrencia"]) != list:
					agregarElemento["indiceOcurrencia"] = [agregarElemento["indiceOcurrencia"]]
				agregarElemento["indiceOcurrencia"].append(resultado["Archivos"]["indiceOcurrencia"])
				indiceNuevo = True
				listaArchivos.append(agregarElemento)
			else:
				listaArchivos.append(agregarElemento)
		if not indiceNuevo:
			listaArchivos.append(resultado["Archivos"])
		collection.find_one_and_update({"Nombre": resultado["Nombre"]},{"$set": {"Archivos": listaArchivos}}, upsert=True)
	else:
		collection.insert(resultado)
def MainNERalias():
	'''
	Flujo inicial del programa
	'''
	regexpParentesis = re.compile("\((.*?)\)")
	for fname in os.listdir(path_docx):
		document = {} #document será el documento que insertemos en la BD, en la collection Entidades
		fullpath = os.path.join(path_docx, fname)
		print ("Archivo: " + fullpath + "\n")
		textoPlano = docx2txt.process(fullpath)
		for element in regexpParentesis.finditer(textoPlano):
			indiceOcurrencia = element.start() #element.start() tiene el index del 1er elemento donde hubo match
			candidato = element.group() #element.group() tiene el match en sí (el candidato)
			parrafo = obtenerContexto(indiceOcurrencia,textoPlano)
			resultado = aplicarReglasAlias(candidato,parrafo,fname,indiceOcurrencia)
			if resultado:
				insertarEnBD(resultado)
			else:
				print("No hubo entidad \n")
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
				insertarEnBD(resultado)
		diccionarioMunicipios(textoPlano,fname)
