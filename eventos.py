# -*- coding: utf-8 -*-
# Autor: Guillermo López Velarde González
import subprocess
import re
import os
import docx2txt
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.NERLegales
collection = db.Entidades
path_docx = "Evaluacion/CorpusEval"

def freeling():
    path_docx = "DOCX"
    for fname in os.listdir(path_docx):
        fullpath = os.path.join(path_docx, fname)
        print ("Archivo: " + fullpath + "\n")
        textoPlano = docx2txt.process(fullpath)
        with open("DOCX_txt/"+fname+".txt","w") as entrada:
            entrada.write(textoPlano)
        with open("DOCX_txt/"+fname+".txt","r") as entrada:
            salida = open("eventos_salidas/"+ fname.replace(".docx","") + "salidaFreeling.txt","w+")
            subprocess.call('analyzer_client 50005',stdin=entrada,stdout=salida,shell=True)
            salida.close()
def obtenerOraciones():
    for fname in os.listdir("eventos_salidas"):
        fullpath = os.path.join("eventos_salidas", fname)
        with open(fullpath, "r") as entrada:
            lineasTexto = entrada.readlines()
        palabras = []
        sentences = {}
        sentences[fname.replace("salidaFreeling.txt","")] = []
        tieneFecha = False
        tieneVerbo = False
        verbos = ["emitió","otorgó","presentó","publicó","solicitó"]
        for linea in lineasTexto:
            if linea == "":
                print("Linea Vacia")
            if linea != "\n":
                elementos = linea.split()
                if len(elementos) == 4:
                    if elementos[2] == "W":
                        tieneFecha = True
                    if elementos[0].lower() in verbos:
                        tieneVerbo = True
                    palabra = elementos[0]
                    palabras.append(palabra)
            else:
                if tieneFecha and tieneVerbo:
                    sentence = ' '.join(palabras)
                    sentence = sentence.replace("_"," ")
                    sentence = sentence.replace(" , "," ")
                    sentence = sentence.replace(" ( ", " ")
                    sentence = sentence.replace(" ) ", " ")
                    sentence = sentence.replace(" .", ".")
                    sentence = sentence.replace(" ;", ";")
                    sentence = sentence.replace(" -", "-")
                    if len(sentence) < 2000:
                        sentences[fname.replace("salidaFreeling.txt","")].append(sentence)
                tieneFecha = False
                tieneVerbo = False
                palabras = []
    return sentences
def buscarQuien(sentence,expresionesQuien):
    quien = ""
    exp = 0
    for expresion in expresionesQuien:
        exp = exp + 1
        quien = re.search(expresion,sentence)
        if quien:
            print (exp)
            return quien.group(1)
    return ""
def buscarFecha(sentence):
    fecha = ""
    listaLineas = []
    with open("entrada.txt","w+") as entrada:
        entrada.write(sentence)
    with open("entrada.txt","r") as entrada:
        salida = open("salida.txt","w")
        subprocess.call('analyzer_client 50005', stdin=entrada, stdout=salida, shell=True)
        salida.close()
    with open("salida.txt","r") as salida:
        lineas = salida.readlines()
    for linea in lineas:
        elementos = linea.split()
        if len(elementos) == 4:
            if elementos[2] == "W":
                fecha = elementos[0].replace("_"," ")
                os.remove("entrada.txt")
                os.remove("salida.txt")
                return fecha
def buscarAQuien(sentence,expresionesAQuien):
    AQuien = ""
    exp = 0
    for expresion in expresionesAQuien:
        exp = exp + 1
        AQuien = re.search(expresion,sentence)
        if AQuien:
            print (exp)
            return AQuien.group(1)
    return ""
def buscarQue(sentence,expresionesQue):
    Que = ""
    exp = 0
    for expresion in expresionesQue:
        exp = exp + 1
        Que = re.search(expresion,sentence)
        if Que:
            print (exp)
            return Que.group(1)
    return ""
def buscarDonde(sentence,expresionesDonde):
    Donde = ""
    exp = 0
    for expresion in expresionesDonde:
        exp = exp + 1
        Donde = re.search(expresion,sentence)
        if Donde:
            print (exp)
            return Donde.group(1)
    return ""
def obtenerExpresionQuien(fname,fecha, verbo):
    #Obtener lista de entidades de la base de datos
    entidades = []
    entidadCursor = collection.find({"$and": [{"$or": [{"Clase":"Persona"},{"Clase":"Organización"}]},{"Archivos.Nombre":fname}]},{"Nombre":1, "_id":0})
    for element in entidadCursor:
        for key, value in element.items():
            entidades.append(value)
    #Obtener lista de alias
    listaAlias = set()
    aliasCursor = collection.find({"$and": [{"$or": [{"Clase":"Persona"},{"Clase":"Organización"}]},{"Archivos.Nombre":fname}]},{"Archivos.Alias":1,"_id":0})
    for element in aliasCursor:
        for key, value in element.items():
            if isinstance(value, list):
                value = list(value)
            for alias in value:
                if isinstance(alias, str):
                    texto = alias
                    alias = {}
                    alias["Alias"] = texto
                elif alias["Alias"] != "":
                    listaAlias.add(alias["Alias"])
    listaAlias = list(listaAlias)
    #Obtener expresion regular con las entidades
    cadenaEntidades = r"("
    for entidad in entidades:
        entidad = re.escape(entidad)
        cadenaEntidades = cadenaEntidades + entidad + r"|"
    for alias in listaAlias:
        alias = re.escape(alias)
        cadenaEntidades = cadenaEntidades + alias + r"|"
    cadenaEntidades = cadenaEntidades + r")"
    cadenaEntidades = cadenaEntidades.replace("|)",")")
    #Obtener expresiones regulares completas, y devolver en una lista
    expresionQuien1 = r"\brepresentante legal de .*? ?" + "(" + cadenaEntidades + " )"
    expresionQuien2 = r"\bpor medio de .*? ?" + "(" + cadenaEntidades + " )"
    expresionQuien3 = r"\ba través de .*? ?" + "(" + cadenaEntidades + " )"
    expresionQuien4 = r"\b"+ fecha +".*?" + "mediante .*? ?" + "(" + cadenaEntidades + " )" + ".*?" + verbo
    expresionQuien5 = r"\b" + fecha + " .*? ?" + "(" + cadenaEntidades + ")" + " .*?" + verbo
    regexQuien1 = re.compile(expresionQuien1)
    regexQuien2 = re.compile(expresionQuien2)
    regexQuien3 = re.compile(expresionQuien3)
    regexQuien4 = re.compile(expresionQuien4)
    regexQuien5 = re.compile(expresionQuien5)
    expresionesQuien = [regexQuien1,regexQuien2,regexQuien3,regexQuien4,regexQuien5]
    return expresionesQuien
def obtenerExpresionAQuien(fname,verbo):
    #Obtener lista de entidades de la base de datos
    entidades = []
    entidadCursor = collection.find({"$and": [{"$or": [{"Clase":"Persona"},{"Clase":"Organización"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Nombre":1, "_id":0})
    for element in entidadCursor:
        for key, value in element.items():
            entidades.append(value)
    #Obtener lista de alias
    listaAlias = set()
    aliasCursor = collection.find({"$and": [{"$or": [{"Clase":"Persona"},{"Clase":"Organización"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Archivos.Alias":1,"_id":0})
    for element in aliasCursor:
        for key, value in element.items():
            if isinstance(value, list):
                value = list(value)
            for alias in value:
                if isinstance(alias, str):
                    texto = alias
                    alias = {}
                    alias["Alias"] = texto
                elif alias["Alias"] != "":
                    listaAlias.add(alias["Alias"])
    listaAlias = list(listaAlias)
    #Obtener expresion regular con las entidades
    cadenaEntidades = r"("
    for entidad in entidades:
        entidad = re.escape(entidad)
        cadenaEntidades = cadenaEntidades + entidad + r"|"
    for alias in listaAlias:
        alias = re.escape(alias)
        cadenaEntidades = cadenaEntidades + alias + r"|"
    cadenaEntidades = cadenaEntidades + r")"
    cadenaEntidades = cadenaEntidades.replace("|)",")")
    #Obtener expresiones regulares completas, y devolver en una lista
    expresionAQuien1 = r"\bante .*? ?" + "(" + cadenaEntidades + " )"
    expresionAQuien3 = r"\ba quien .*? ?" + "(" + cadenaEntidades + " )"
    expresionAQuien2 = r"\ben favor de .*? ?" + "(" + cadenaEntidades + " )"
    expresionAQuien4 = r"\b" + verbo + " a .*?" + "(" + cadenaEntidades + " )"
    regexAQuien1 = re.compile(expresionAQuien1)
    regexAQuien2 = re.compile(expresionAQuien2)
    regexAQuien3 = re.compile(expresionAQuien3)
    regexAQuien4 = re.compile(expresionAQuien4)
    expresionesAQuien = [regexAQuien1,regexAQuien2,regexAQuien3,regexAQuien4]
    return expresionesAQuien
def obtenerExpresionQue(fname):
    #Obtener lista de entidades de la base de datos
    entidades = []
    entidadCursor = collection.find({"$and": [{"$or": [{"Clase":"Ley"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Nombre":1, "_id":0})
    for element in entidadCursor:
        for key, value in element.items():
            entidades.append(value)
    #Obtener lista de alias
    listaAlias = set()
    aliasCursor = collection.find({"$and": [{"$or": [{"Clase":"Ley"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Archivos.Alias":1,"_id":0})
    for element in aliasCursor:
        for key, value in element.items():
            if isinstance(value, list):
                value = list(value)
            for alias in value:
                if isinstance(alias, str):
                    texto = alias
                    alias = {}
                    alias["Alias"] = texto
                elif alias["Alias"] != "":
                    listaAlias.add(alias["Alias"])
    listaAlias = list(listaAlias)
    #Obtener expresion regular con las entidades
    cadenaEntidades = r"("
    for entidad in entidades:
        entidad = re.escape(entidad)
        cadenaEntidades = cadenaEntidades + entidad + r"|"
    for alias in listaAlias:
        alias = re.escape(alias)
        cadenaEntidades = cadenaEntidades + alias + r"|"
    cadenaEntidades = cadenaEntidades + r")"
    cadenaEntidades = cadenaEntidades.replace("|)",")")
    expresionQue1 = r"\b(opinión .*? ?" + cadenaEntidades + ")"
    expresionQue2 = r"\b(opinión .*? )"
    expresionQue3 = r"\b" + verbo + " .*?" + "(" + cadenaEntidades + " )"
    regexQue1 = re.compile(expresionQue1)
    regexQue2 = re.compile(expresionQue2)
    regexQue3 = re.compile(expresionQue3)
    expresionesQue = [regexQue1,regexQue2,regexQue3]
    return expresionesQue
def obtenerExpresionDonde(fname):
    #Obtener lista de entidades de la base de datos
    entidades = []
    entidadCursor = collection.find({"$and": [{"$or": [{"Clase":"Otro"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Nombre":1, "_id":0})
    for element in entidadCursor:
        for key, value in element.items():
            entidades.append(value)
    salida = []
    for s in entidades:
        if not any([s in r for r in entidades if s != r]):
            salida.append(s)
    entidades = salida
    #Obtener lista de alias
    listaAlias = set()
    aliasCursor = collection.find({"$and": [{"$or": [{"Clase":"Otro"},{"Clase":"Documento"}]},{"Archivos.Nombre":fname}]},{"Archivos.Alias":1,"_id":0})
    for element in aliasCursor:
        for key, value in element.items():
            if isinstance(value, list):
                value = list(value)
            for alias in value:
                if isinstance(alias, str):
                    texto = alias
                    alias = {}
                    alias["Alias"] = texto
                elif alias["Alias"] != "":
                    listaAlias.add(alias["Alias"])
    listaAlias = list(listaAlias)
    salida = []
    for s in listaAlias:
        if not any([s in r for r in listaAlias if s != r]):
            salida.append(s)
    listaAlias = salida
    #Obtener expresion regular con las entidades
    cadenaEntidades = r"("
    for entidad in entidades:
        entidad = re.escape(entidad)
        cadenaEntidades = cadenaEntidades + entidad + r"|"
    for alias in listaAlias:
        alias = re.escape(alias)
        cadenaEntidades = cadenaEntidades + alias + r"|"
    cadenaEntidades = cadenaEntidades + r")"
    cadenaEntidades = cadenaEntidades.replace("|)",")")
    expresionDonde1 = r"\ben .*? ?" + "(" + cadenaEntidades + " )"
    regexDonde1 = re.compile(expresionDonde1)
    expresionesDonde = [regexDonde1]
    return expresionesDonde

sentences = obtenerOraciones()
for key,value in sentences.items():
    print("Archivo: " + key)
    for sentence in value:
        if "emitió" in sentence:
            verbo = "emitió"
            oracion = sentence
            fecha = buscarFecha(oracion)
            expresionesQuien = obtenerExpresionQuien(key,fecha,verbo)
            expresionesQue = obtenerExpresionQue(key)
            quien = buscarQuien(oracion,expresionesQuien)
            oracion = oracion.replace(quien,"")
            Que = buscarQue(oracion,expresionesQue)
            print (sentence)
            print ("Verbo: emitió")
            print ("Fecha: " + fecha)
            print ("Quien: " + quien)
            print ("Que: " + Que)
            print("\n")
        if "otorgó" in sentence:
            verbo = "otorgó"
            oracion = sentence
            fecha = buscarFecha(oracion)
            expresionesQuien = obtenerExpresionQuien(key,fecha,verbo)
            expresionesAQuien = obtenerExpresionAQuien(key,verbo)
            expresionesQue = obtenerExpresionQue(key)
            quien = buscarQuien(oracion,expresionesQuien)
            oracion = oracion.replace(quien,"")
            AQuien = buscarAQuien(oracion,expresionesAQuien)
            oracion = oracion.replace(AQuien,"")
            Que = buscarQue(oracion,expresionesQue)
            print (sentence)
            print ("Verbo: otorgó")
            print ("Fecha: " + fecha)
            print ("Quien: " + quien)
            print ("A Quien: " + AQuien)
            print ("Que: " + Que)
            print("\n")
        if "presentó" in sentence:
            verbo = "presentó"
            oracion = sentence
            fecha = buscarFecha(oracion)
            expresionesQuien = obtenerExpresionQuien(key,fecha,verbo)
            expresionesAQuien = obtenerExpresionAQuien(key,verbo)
            expresionesQue = obtenerExpresionQue(key)
            quien = buscarQuien(oracion,expresionesQuien)
            oracion = oracion.replace(quien,"")
            AQuien = buscarAQuien(oracion,expresionesAQuien)
            oracion = oracion.replace(AQuien,"")
            Que = buscarQue(oracion,expresionesQue)
            print (sentence)
            print ("Verbo: presentó")
            print ("Fecha: " + fecha)
            print ("Quien: " + quien)
            print ("A Quien: " + AQuien)
            print ("Que: " + Que)
            print("\n")
        if "publicó" in sentence:
            verbo = "publicó"
            oracion = sentence
            fecha = buscarFecha(oracion)
            expresionesQuien = obtenerExpresionQuien(key,fecha,verbo)
            expresionesDonde = obtenerExpresionDonde(key)
            expresionesQue = obtenerExpresionQue(key)
            quien = buscarQuien(oracion,expresionesQuien)
            oracion = oracion.replace(quien,"")
            donde = buscarDonde(oracion,expresionesDonde)
            oracion = oracion.replace(donde,"")
            Que = buscarQue(oracion,expresionesQue)
            print (sentence)
            print ("Verbo: publicó")
            print ("Fecha: " + fecha)
            print ("Quien: " + quien)
            print ("Donde: " + donde)
            print ("Que: " + Que)
            print("\n")
        if "solicitó" in sentence:
            verbo = "solicitó"
            oracion = sentence
            fecha = buscarFecha(oracion)
            expresionesQuien = obtenerExpresionQuien(key,fecha,verbo)
            expresionesAQuien = obtenerExpresionAQuien(key,verbo)
            expresionesQue = obtenerExpresionQue(key)
            quien = buscarQuien(oracion,expresionesQuien)
            oracion = oracion.replace(quien,"")
            AQuien = buscarAQuien(oracion,expresionesAQuien)
            oracion = oracion.replace(AQuien,"")
            Que = buscarQue(oracion,expresionesQue)
            print (sentence)
            print ("Verbo: solicitó")
            print ("Fecha: " + fecha)
            print ("Quien: " + quien)
            print ("A Quien: " + AQuien)
            print ("Que: " + Que)
            print("\n")
