# -*- coding: utf-8 -*-
#GILKATON
import subprocess
from xml.etree.cElementTree import XML
import xml.etree.ElementTree as XML2
import zipfile
import re
import csv

#encoding utf8 para que no me marque errores :S
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#se asignan los namespace
WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
def get_docx_text(path):
    #se abre con zipfile el archivo en .docx
    document = zipfile.ZipFile(path)
    #se lee el xml con .read
    xml_content = document.read('word/document.xml')
    #cerramos el documento
    document.close()
    #parseamos el arbol xml
    tree = XML(xml_content)
    #creamos una lista vacia de parrafos
    paragraphs = []
    #por cada parrafo en el arbol que tiene el contenido, y que tiene de namespace PARA
    for paragraph in tree.getiterator(PARA):
        #El texto es igual al texto, donde cada nodo es cada palabra del parrafo
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        #si texts existe (o sea sí, a menos que haya un error)
        if texts:
            #unimos toda la lista de palabras en un solo elemento
            paragraphs.append(''.join(texts))
    #devolvemos los parrafos unidos por doble salto de línea por parrafo
    return '\n\n'.join(paragraphs)

#textoPlano tiene el texto del documento
textoPlano = get_docx_text('DOF_P_IFT_250117_12_Acc.docx').encode('utf-8')
#creamos un .txt con el texto que acabamos de sacar
f = open('texto.txt','w')
f.write(textoPlano)
f.close()
######################FREELING######################
#reabrimos el archivo para meterlo a freeling
textInput = open('texto.txt')
#Abrimos el archivo xml a escribir
xmlOutput = open("file_out.xml", "w")
#Corremos el comando con el archivo de configuración para español (es.cfg) y pedimos un analisis Tagged (PoS), y pedimos el output en formato XML
subprocess.call("analyze -f es.cfg --ner --nec --outlv parsed --output xml", stdin=textInput, stdout=xmlOutput, shell=True)
#Cerramos el archivo con permisos de escritura
xmlOutput.close()
textInput.close()
################PONER ROOT EN XML#############
with open("file_out.xml", 'r+') as f:
    content = f.read()
    f.seek(0)
    f.write('<raiz>' + content)
with open("file_out.xml",'a+') as f:
    f.write('\n  </raiz>')

#El archivo file_out.xml tiene nuestro word procesado por freeling
#parseamos el arbol en variable arbol
arbol = XML2.parse('file_out.xml')
#obtenemos el root
root = arbol.getroot()
##############################################TABLA 1##########################################
#creamos diccionario que guardará todo
tabla1 = dict()
tabla2 = dict()
#la llave será la entidad, y el valor, un arreglo donde [0] es la abreviación, [1] el contexto antes
#y [2] el después
###################PARENTESIS############
#Se obtiene el único contenido de paréntesis
listaParentesis = list(set(re.findall('\((.*?)\)',textoPlano)))
for element in listaParentesis:
    print element
    contador = 0
    #elimino los artículos
    element = element.replace("en adelante, ","")
    element = element.replace("en lo sucesivo, ", "")
    element = element.replace("la ","")
    element = element.replace("del ","dl ")
    element = element.replace("el ","")
    element = element.replace("dl ","del ")
    element = element.replace("los ","")
    element = element.replace("las ","")
    element = element.replace('”',"")
    element = element.replace('“',"")
    element = element.replace('"',"")
    #Si el contenido del paréntesis es mayúscula y no tiene espacios
    #significa que son siglas
    if element.isupper() and " " not in element and len(element)<7:
        #Indice Final porque hasta acá vamos a buscar un nombre de entidad.
        indiceF = textoPlano.find(element)
        #Nos ponemos un lugar atrás con el indice I, que es el que se colocará 10 palabras antes para
        #buscar mayúsculas
        indiceI = indiceF
        #Vamos a agarrar 10 palabras antes del paréntesis
        while contador != 30:
            if textoPlano[indiceI] == " ":
                contador = contador + 1
            indiceI = indiceI - 1
            #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
            #y seguimos contando hasta las 10 palabras
            cadenaAnterior = textoPlano[indiceI:indiceF]

        #agarraremos 10 palabras después del paréntesis, para el contexto
        indiceI = textoPlano.find(element) + len(element)
        indifeF = indiceI
        contador = 0
        while contador != 10:
            if textoPlano[indiceF] == " ":
                contador = contador + 1
            indiceF = indiceF + 1
            #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
            #y seguimos contando hasta las 10 palabras

        #10 palabras después de nuestro paréntesis con siglas
        cadenaPosterior = textoPlano[indiceI:indiceF]
        #Quitamos primeros 2 caracteres por NO SE pero es basura.
        cadenaAnterior = cadenaAnterior[2:]
        #Obtenemos el match de la primera letra
        #validar acentos. Se va a buscar ambas, el elemento, y el
        #acento puesto. El que tenga el índice más grande es el bueno.
        acentoPuesto = ""
        indiceEntidadI2 = 0
        #Buscams primero sin acentos
        if element[0] in cadenaAnterior:
            indiceEntidadI = cadenaAnterior.find(element[0])
        #Buscamos con acentos
        if element[0] == 'a':
            acentoPuesto = 'á'
        if element[0] == 'e':
            acentoPuesto = 'é'
        if element[0] == 'i':
            acentoPuesto = 'í'
        if element[0] == 'o':
            acentoPuesto = 'ó'
        if element[0] == 'u':
            acentoPuesto = 'ú'
        if element[0] == 'A':
            acentoPuesto = 'Á'
        if element[0] == 'E':
            acentoPuesto = 'É'
        if element[0] == 'I':
            acentoPuesto = 'Í'
        if element[0] == 'O':
            acentoPuesto = 'Ó'
        if element[0] == 'U':
            acentoPuesto = 'Ú'
        try:
            if acentoPuesto in cadenaAnterior:
                indiceEntidadI2 = cadenaAnterior.find(acentoPuesto)
        except NameError:
            pass
        try:
            if indiceEntidadI2 > indiceEntidadI:
                indiceEntidadI = indiceEntidadI2
        except NameError:
            #Significa que no hay nada que pueda significar esas siglas, así que bai
            indiceEntidadI = 0
            pass
        if not indiceEntidadI == 0:
            Entidad = cadenaAnterior[indiceEntidadI:]
            print "parentesis, sólo siglas"
            #quitamos bug que quiensabeporquesale
            Entidad = Entidad.replace("”","")
            Entidad = Entidad.replace("("," ")
            Entidad = Entidad.replace("en lo sucesivo", "")
            Entidad = Entidad.replace("en adelante", "")
            Entidad = Entidad.replace(")", " ")
            Entidad = Entidad.replace(" , ", "")
            Entidad = Entidad.replace("“", "")
            if "_" not in Entidad:
                if not Entidad.isupper():
                    if Entidad == "Diario Oficial de la Federación el ":
                        Entidad = "Diario Oficial de la Federación"
                    print Entidad
                    print element
                    #guardo en la tabla 1, los valores que saqué, gracias a cristo jesus. T_T
                    tabla1[Entidad] = [element,cadenaAnterior,cadenaPosterior]

    #De otra forma, buscamos la palabra
    #en las 10 palabras anteriores, y contamos de ahí para adelante.
    else:
        #encuentro el índice de este caso
        indiceF = textoPlano.find('(' + element + ')')
        lenOriginal = len(element)
        #Si no hay espacios, después de haber quitado los artículos y "en lo sucesivo, " y "en adelante, "
        #y si no son puras mayusculas, y la primer letra es mayúscula
        if " " not in element and not element.isupper() and element[0].isupper():
            #Nos ponemos un lugar atrás con el indice I, que es el que se colocará 10 palabras antes para
            #buscar mayúsculas
            indiceI = indiceF
            #Vamos a agarrar 10 palabras antes del paréntesis
            while contador != 30:
                if textoPlano[indiceI] == " ":
                    contador = contador + 1
                indiceI = indiceI - 1
                cadenaAnterior = textoPlano[indiceI:indiceF+1]

            #agarraremos 10 palabras después del paréntesis, para el contexto
            indiceI = indiceF + lenOriginal + 1
            indifeF = indiceI
            contador = 0
            while contador != 10:
                if textoPlano[indiceF] == " ":
                    contador = contador + 1
                indiceF = indiceF + 1
                #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
                #y seguimos contando hasta las 10 palabras

            #10 palabras después de nuestro paréntesis con siglas
            cadenaPosterior = textoPlano[indiceI:indiceF]

            #Quitamos primeros 2 caracteres por NO SE pero es basura.
            cadenaAnterior = cadenaAnterior[2:]

            #Obtenemos el match de la palabra en cuestión letra
            if element in cadenaAnterior:
                indiceEntidadI = cadenaAnterior.find(element)
                Entidad = cadenaAnterior[indiceEntidadI:]
                #guardo en la tabla 1, los valores que saqué, gracias a cristo jesus. T_T
                print "parentesis, con otras palabras, abreviación de una palabra"
                Entidad = Entidad[:-2]
                #quitamos bug que quiensabeporquesale
                Entidad = Entidad.replace("”","")
                print Entidad
                print element
                tabla1[Entidad] = [element,cadenaAnterior,cadenaPosterior]
        #Si sí hay espacios en la abreviación, hay que ver si la primera palabra
        #empieza con mayúscula, y si no son todas mayúsculas (o sea que no
        #sean siglas otra vez veda. 0 elegancia.nohaytiempo.)
        else:
            pattern = r'[A-Z].+? (para|el|de|la|los|y|las|del)*(para|el|de|la|los|y|las|del)* [A-Z].+?'
            #Si tiene el patron de que la 1ra es mayuscula
            if re.match(pattern,element):
                Indice1 = []
                Indice1.append(textoPlano.find(element))
                Indice1.append(textoPlano.find(element + "”"))
                Indice1.append(textoPlano.find(element + '"'))
                Indice1.append(textoPlano.find(element + ')'))
                indiceI = max(Indice1)
                #Nos ponemos un lugar atrás con el indice I, que es el que se colocará 10 palabras antes para
                #buscar mayúsculas
                indiceF = indiceI
                #Vamos a agarrar 25 palabras antes del paréntesis
                while contador != 48:
                    if textoPlano[indiceI] == " ":
                        contador = contador + 1
                    indiceI = indiceI - 1
                    #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
                    #y seguimos contando hasta las 10 palabras
                    cadenaAnterior = textoPlano[indiceI:indiceF]

                #agarraremos 10 palabras después del paréntesis, para el contexto
                indiceI = textoPlano.find(element) + len(element)
                indifeF = indiceI
                contador = 0
                while contador != 20:
                    if textoPlano[indiceF] == " ":
                        contador = contador + 1
                    indiceF = indiceF + 1
                    #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
                    #y seguimos contando hasta las 10 palabras

                #10 palabras después de nuestro paréntesis con siglas
                cadenaPosterior = textoPlano[indiceI:indiceF]
                #Quitamos primeros 2 caracteres por NO SE pero es basura.
                cadenaAnterior = cadenaAnterior[2:]
                #Obtenemos el match de la primera letra
                #validar acentos. Se va a buscar ambas, el elemento, y el
                #acento puesto. El que tenga el índice más grande es el bueno.
                acentoPuesto = ""
                indiceEntidadI2 = 0
                #Buscams primero sin acentos
                if element[0] in cadenaAnterior:
                    indiceEntidadI = cadenaAnterior.find(element[0])
                #Buscamos con acentos
                if element[0] == 'a':
                    acentoPuesto = 'á'
                if element[0] == 'e':
                    acentoPuesto = 'é'
                if element[0] == 'i':
                    acentoPuesto = 'í'
                if element[0] == 'o':
                    acentoPuesto = 'ó'
                if element[0] == 'u':
                    acentoPuesto = 'ú'
                if element[0] == 'A':
                    acentoPuesto = 'Á'
                if element[0] == 'E':
                    acentoPuesto = 'É'
                if element[0] == 'I':
                    acentoPuesto = 'Í'
                if element[0] == 'O':
                    acentoPuesto = 'Ó'
                if element[0] == 'U':
                    acentoPuesto = 'Ú'
                try:
                    if acentoPuesto in cadenaAnterior:
                        indiceEntidadI2 = cadenaAnterior.find(acentoPuesto)
                except NameError:
                    pass
                if indiceEntidadI2 > indiceEntidadI:
                    indiceEntidadI = indiceEntidadI2

                Entidad = cadenaAnterior[indiceEntidadI:]
                print "parentesis, abreviatura de muchas palabras"
                #quitamos bug que quiensabeporquesale
                Entidad = Entidad.replace("”","")
                Entidad = Entidad.replace("("," ")
                Entidad = Entidad.replace("en lo sucesivo", "")
                Entidad = Entidad.replace("en adelante", "")
                Entidad = Entidad.replace(")", " ")
                Entidad = Entidad.replace(" , ", "")
                Entidad = Entidad.replace("“", "")
                #Intento desesperado por filtrar direcciones
                if "Delegación" not in Entidad:
                    #Intento por quitar tablas
                    if "-" not in Entidad:
                        if not re.match(r'[0-9]',Entidad) and re.match(r'[0-9]',cadenaAnterior):
                            if not Entidad.isupper():
                                if Entidad == "Programa de Trabajo para Reorganizar el Espectro Radioeléctrico a Estaciones de Radio y Televisión el ":
                                    Entidad = "Programa de Trabajo para Reorganizar el Espectro Radioeléctrico a Estaciones de Radio y Televisión"
                                print Entidad
                                print element
                                #guardo en la tabla 1, los valores que saqué, gracias a cristo jesus. T_T
                                tabla1[Entidad] = [element,cadenaAnterior,cadenaPosterior]

#Si no son paréntesis, entonces hay que buscar las abreviaciones por si mismas
############################INCISOS##########################
#Buscamos todo lo que esté encerrado en incisos y puntos y guiones
pattern = r'[a-zA-Z]\).+?\.-'
#lo guardamos en la variable Incisos
Incisos = re.findall(pattern,textoPlano)
#Les quitamos el inciso, y los .- a cada uno.
tokens = []
for inciso in Incisos:
    inciso = inciso.replace(" ","")
    tokens.append(inciso[2:-2])

print tokens
#por cada token
for token in tokens:
    #Encontramos el índice dentro del texto donde aparece.
    indiceI = textoPlano.find(token) + len(token)
    #Si después de la longitud del token, hay un . o : , es abreviación.
    #Si hay un . , hay que checar que luego haya un - para que sea abreviación
    #Si no hay nada, no es nada. Fin.
    try:
        if textoPlano[indiceI] == "." and textoPlano[indiceI+1] == "-":
            indiceF = indiceI
            contador = 0
            #Mientras no encontremos el punto final
            while textoPlano[indiceF+1] != ".":
                indiceF = indiceF + 1
            #guardamos en cadenaAnterior el textoPlano desde el indiceI hasta el F
            #y seguimos contando hasta las 10 palabras
            #10 palabras después de nuestro paréntesis con siglas
            cadenaPosterior = textoPlano[indiceI:indiceF+1]
            #Obtenemos el match de la primera letra
            if token[0] in cadenaPosterior:
                indiceEntidadI = cadenaPosterior.find(token[0])
            Entidad = cadenaPosterior[indiceEntidadI:]
            print Entidad
            print token
            #guardo en la tabla 1, los valores que saqué, gracias a cristo jesus. T_T
            print "Incisos, sin nada antes"
            print Entidad
            print token
            tabla1[Entidad] = [token,"",cadenaPosterior]
        #Si en vez de .- es : entonces
        elif textoPlano[indiceI+len(token)] == ":":
            print token
    except IndexError:
        pass


########################################## ESCRIBIR CSV ################################################
with open('entidades.csv', 'w') as csvfile:
    fieldnames = ['Contexto', 'Entidad', 'Abreviatura']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in tabla1.iteritems():
        writer.writerow({'Contexto': ""+value[1]+value[0]+value[2] , 'Entidad': key, 'Abreviatura': value[0]})

#print tabla1['Instituto']
#entidad tiene la lista de entidades sin separar las abreviaciones


########################################FECHAS###########################################
#print entidad
fecha = []
for node in arbol.findall('./sentence/token'):
    if node.attrib['tag'] == "W":
        element = node.attrib['lemma'].encode('utf-8')
        element = element.replace("_"," ")
        fecha.append(element)
        id = node.attrib['id'].encode('utf-8')

listaFechas = []
for element in fecha:
    element = element.replace("?","")
    element = element.replace(":","")
    element = element.replace(".","")
    element = element[1:-1]
    pattern = r'[0-9]*[0-9]/[0-9]*[0-9]/[0-9][0-9][0-9][0-9]'
    if re.match(pattern,element):
        print element
        listaFechas.append(element)

print listaFechas

#aquí hay que encontrar el verbo principal TODAVIA NO FUNCIONA
idFechas = dict()
for node in arbol.findall('./sentence/token'):
    for fecha in listaFechas:
        if fecha in node.attrib['lemma']:
            #agarro el 1 porque es el número del ID
            idFechas[fecha] = list(node.attrib['id'][1])
#idFechas tiene como llave, las fechas, y como key, el ID de la oración :)
print idFechas
tagAnterior = ""
for node in arbol.findall('./sentence'):
    for key in idFechas:
        if node.attrib['id'] == idFechas[key][0]:
            node.find("token")
            for x in node.iter("token"):
                if x.attrib["pos"] == "verb" and x.attrib["type"] == "main" and re.match(r'VMIS.+?', x.attrib["tag"]):
                    if len(idFechas[key]) < 2:
                        idFechas[key].append(x.attrib["lemma"])
                if re.match(r'VSIS.+?', x.attrib["tag"]):
                    tagAnterior = x.attrib["tag"]
                else:
                    tagAnterior = ""
                if re.match(r'VMP0.+?',x.attrib["tag"]) and re.match(r'VSIS.+?', tagAnterior):
                    if len(idFechas[key]) < 2:
                        idFechas[key].append(x.attrib["lemma"])
            #Si al final, el lemma queda vacío
            if len(idFechas[key]) == 0:
                for x in node.iter("token"):
                    if x.attrib["pos"] == "verb" and not re.match(r'VSIS.+?',x.attrib["tag"]):
                        idFechas[key].append(x.attrib["lemma"])
####################Contexto####################
for node in arbol.findall('./sentence'):
    for key in idFechas:
        if node.attrib['id'] == idFechas[key][0]:
            node.find("token")
            for x in node.iter("token"):
                idFechas[key].append(x.attrib["form"])
        idFechas[key][2:] = [' '.join(idFechas[key][2:])]

###################QUIEN##################
for node in arbol.findall('./sentence'):
    for key in idFechas:
        node.find("token")
        for x in node.iter("token"):
            if re.match(r'NP00[A-Z]00', x.attrib['tag']):
                idFechas[key].append(x.attrib["form"])
        #ya estamos en la oración

#Quitar guiones bajo de los QUIEN
for key,value in idFechas.iteritems():
    value[3] = value[3].replace("_"," ")
#Quitar los guiones bajo del contexto
for key,value in idFechas.iteritems():
    value[2] = value[2].replace("_"," ")

#Si lo dejo vacio, lo lleno con el primero
for key,value in idFechas.iteritems():
    if "_" in value[1] or " " in value[1]:
        value[1] = ""


###############PARA QUE#################
for key, value in idFechas.iteritems():
    if "para" in value[2]:
        print "HUBO UN PARAAAAAA en"
        print idFechas[key]
        indiceParaI = value[2].find("para") + len("para")
        idFechas[key].append(value[2][indiceParaI:])
    if "mediante el cual" in value[2]:
        indiceParaI = value[2].find("mediante el cual") + len("mediante el cual")
        idFechas[key].append(value[2][indiceParaI:])
    if "con el fin de" in value[2]:
        indiceParaI = value[2].find("con el fin de") + len("con el fin de")
        idFechas[key].append(value[2][indiceParaI:])
    if "con la finalidad de" in value[2]:
        indiceParaI = value[2].find("con la finalidad de") + len("con la finalidad de")
        idFechas[key].append(value[2][indiceParaI:])

########################################## ESCRIBIR CSV ################################################
with open('sucesos.csv', 'w') as csvfile:
    fieldnames = ['Contexto', 'Fecha', 'Lema','Quien','Que','Donde','A quien','Para que']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in idFechas.iteritems():
        writer.writerow({'Contexto': ""+value[2] , 'Fecha': key, 'Lema': ""+value[1], 'Quien': ""+value[3],'Para que': ""+value[4]})


##############################################TABLA 3##############################
###fraccion###

#listaLeyes = list(set(re.findall('(Ley ([A-Za-z])*?)',textoPlano)))
listaLeyes = re.finditer("Ley", textoPlano)
minuscula = 0
cadenaLey = ""
listaLeyes2 = []
for elem in listaLeyes:
    cadenaLey=""
    tokensTexto = textoPlano[elem.start():].split()
    for tokens in tokensTexto:
        if tokens[0].isupper() or tokens == "de" or tokens == "la" or tokens == "los" or tokens == "y" or tokens == "a" or tokens == "las" or tokens == "los" or tokens == "el":
            cadenaLey += " " + tokens
            continue
        else:
            break
    listaLeyes2.append(cadenaLey)

listaLeyes3 = []
for Ley in listaLeyes2:
    if "." in Ley:
        numeroI = Ley.find(".")
        listaLeyes3.append(Ley[:numeroI])
    elif "," in Ley:
        numeroI = Ley.find(",")
        listaLeyes3.append(Ley[:numeroI])
    else:
        listaLeyes3.append(Ley)

listaLeyes3 = list(set(listaLeyes3))

##########################################TABLA 3#####################################
with open('leyes.csv', 'w') as csvfile:
    fieldnames = ['Contexto', 'Leyes', 'Artículos','Fracciones']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for elem in listaLeyes3:
        writer.writerow({'Leyes': elem })

#print tabla1['Instituto']
#entidad tiene la lista de entidades sin separar las abreviaciones
