# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
# Script que obtiene los eventos del conjunto de documentos
#----------------------------------------------------------------------
# Se ejecuta de la siguiente manera:
# python eventos.py [-h] verbo
# -h - para que la salida no use los ids de las entidades ni de los documentos, sino sea el texto
# verbo - el verbo del cual obtener los eventos (la forma, no el lema)
# La salida se escribirá a un archivo de nombre out_<verbo>.csv
#----------------------------------------------------------------------
import sys
import os
import re
import csv
from entidades import collapse_cc_np, filter_np
import argparse

#Obtener argumentos de línea de comandos
parser = argparse.ArgumentParser()
parser.add_argument("verbo", help="Verbo del cual obtener eventos")
parser.add_argument("-l", action="store_true", help="Salida leíble por humanos")
args = parser.parse_args()
verbo = args.verbo
    
class Candidate:
    """
        Esta clase analiza una ventana de tokens e intenta extraer los 4 argumentos: quién, qué, dónde, a quién
    """
    
    def __init__(self, date, window, window_before, sentence, quoted, document, word_count):
        """
            Establece las variables
            date - fecha
            window - ventana despueés del verbo (incluyendo el verbo)
            window_before - ventana antes del verbo
            sentence - toda la oración donde aparece el verbo
            quoted - elemento entrecomillado
            document - nombre del documento donde se encuentra este evento
            word_count - en qué número de palabra ocurre el verbo
        """
        self.date = date
        self.date = self.norm_date()
        self.window = window
        self.window_before = window_before
        self.sentence = sentence
        self.verb = window[0]
        self.quoted = quoted
        self.document = document
        self.word_count = word_count

    def norm_date(self):
        """
            Normaliza la fecha de freeling a formato ISO (aaaa-mm-dd)
        """
        m = re.search("(\d+)/(\d+)/(\d+)", self.date)
        if m:
            return m.group(3).zfill(4) + "-" + m.group(2).zfill(2) + "-" + m.group(1).zfill(2)
        else:
            return self.date

    def get_args(self):
        """
            Hace el procesamiento de la ventana.
            
            Retorna una tupla con los argumentos encontrados
        """
        where = None
        who = None
        what = None
        to_whom = None
        paren = False

        #A QUIÉN
        #Lo que esté después de "a", "ante", "a favor de" es "a quién", pero ese "a" debe estar inmediatamente después del verbo del evento
        #o no inmediatamente después pero que no hay otros verbos enmedio
        #"Ante" puede estar en la parte precedente al verbo
        for i,token in enumerate(self.window_before):
            tok = token.split("/")[0]
            if tok == 'ante':
                for j,token2 in enumerate(self.window_before[i+1:]):
                    if '/NP' in token2:
                        to_whom = token2
                        break
                if to_whom:
                    break
        if not to_whom:
            for i,token in enumerate(self.window):
                if i == 0:
                    continue
                if token == 'a/SP' or "favor_de/" in token or tok == 'ante':
                    blacklist = ["adicional", "referente", "respecto", "correspondiente"]
                    blacklist_tag = ["AQ", "SP"]
                    skip = False
                    for bw in blacklist:
                        if bw in self.window[i-1]:
                            skip = True
                            break
                    else:
                        for bt in blacklist_tag:
                            if "/" + bt in self.window[i-1]:
                                skip = True
                                break
                    if skip:
                        continue
                    for j,token2 in enumerate(self.window[i+1:]):
                        if token2 == 'a/SP' or "favor_de" in token2 or 'ante' in token2:
                            break
                        if '/NP' in token2:
                            to_whom = token2
                            break
                    if to_whom:
                        break
                if '/V' in token:
                    break

        #EN DÓNDE
        #Solo publicó lleva dónde y es después de "en el"
        if self.verb == 'publicó':
            for i,token in enumerate(self.window):
                if token == 'en/SP':
                    if i+1 < len(self.window):
                        for j,token2 in enumerate(self.window[i+1:]):
                            if '/NP' in token2:
                                where = self.window[i+2]
                                break
                        if where:
                            break

        #QUIÉN
        #El sujeto no puede estar en una frase preposicional. Marcar las que se descartan
        sp_stack = []
        who_blacklist = [False] * len(self.window_before)
        for i,token in enumerate(self.window_before):
            if '/SP' in token:
                sp_stack.append(token)
            elif '/NC' in token or '/NP' in token:
                if sp_stack:
                    sp_stack.pop()
                    who_blacklist.append(token)
        #El sujeto más simple es el nombre que está inmediatamente antes del verbo, sin comas ni nada
        if self.window_before:
            token = self.window_before[-1]
            if "/NP" in token and not token in who_blacklist:
                who = token
        #Representante legal de...
        if not who:
            for i,token in enumerate(self.window_before):
                if "representante/" in token:
                    if i+2 < len(self.window_before):
                        if "legal/" in self.window_before[i+1] and "de/" in self.window_before[i+2]:
                            for j,token2 in enumerate(self.window_before[i+3:]):
                                if '/NP' in token2:
                                    who = token2 #(no aplica blacklist por que si está en una frase preposicional)
                                    break
                            if who:
                                break
        #Otro patrón es "SUJETO  a_través_de" y "SUJETO mediante", puede o no haber coma
        if not who:
            for i,token in enumerate(self.window_before):
                if "/NP" in token:
                    if i+1 < len(self.window_before):
                        next = self.window_before[i+1]
                        if next.startswith(",") and len(self.window_before) > i+2:
                            next = self.window_before[i+2]
                        if next.startswith("mediante") or next.startswith("a_través_de") and not who_blacklist[i]:
                            who = token
                            break
        #Otro patrón es "SUJETO ( frase de alias ), "
        if not who:
            for i,token in enumerate(self.window_before):
                if "/NP" in token and len(self.window_before) > i+1:
                    next = self.window_before[i+1]
                    if "Fpa" in next and not who_blacklist[i]:
                        who = token
                        break
        #También puede ser quien aparece inmediatamente después de la fecha
        if not who:
            for i,token in enumerate(self.window_before):
                if i+2 < len(self.window_before):
                    next = self.window_before[i+1]
                    next2 = self.window_before[i+2]
                    if token.startswith('FECHA'):
                        if '/NP' in next or ('/F' in next and '/NP' in next2) and not who_blacklist[i+2]:
                            who = next2
                            break
        #Entidad nombrada que esté entre comas sin ninguna otra cosa más que determinante
        if not who:
            for i in range(len(self.window_before)-1,0,-1):
                if 'Fc' in self.window_before[i]:
                    for j in range(i-1,0,-1):
                        token = self.window_before[j]
                        tag = token.split("/")[1]
                        if '/NP' in token:
                            if not who_blacklist[j]:
                                who = token
                        else:
                            if tag == 'Fc':
                                break
                            elif not tag[0] == 'D':
                                who = None
                                break
                if who:
                    break
        if not who:
            #La primer entidad que no sea de la blacklist
            for i,token in enumerate(self.window_before):
                if 'NP' in token and not who_blacklist[i]:
                    who = token
                    break

        #QUÉ
        #Si hay algo entrecolmillado tomar ese
        if self.quoted:
            what = " ".join(self.quoted)
            if not "Frc" in self.quoted[-1]:
                what += "(...)"
        else:
            #Si no tomar el primer nombre, o participio o infinitivo,  que no esté en una frase preposicional, que no esté entre paréntesis, y que no sea alguna cosa como un inciso
            stack = []
            par_open = False
            for i,token in enumerate(self.window[1:]):
                if 'Fpa' in token:
                    par_open = True
                elif 'Fpt' in token:
                    par_open = False
                if '/SP' in token:
                    stack.append(token)
                names_tags = ['NP', 'NC', 'VMN', 'VMP', 'VMS']
                for ntag in names_tags:
                    if '/' + ntag in token:
                        tok = token.split("/")[0]
                        if len(tok) <= 3 and ntag == 'NC':
                            continue
                        if par_open:
                            continue
                        if stack:
                            stack.pop()
                        else:
                            what = token
                            break
                if what:
                    break

        contexto = " ".join([x.split("/")[0] for x in self.sentence])
        contexto = contexto.replace('"','').replace(",",'')
        self.context = contexto
        #Descomentar esto para mostrar en pantalla lo que encuentra el programa
        #print self.document, self.date, who, self.verb, what, "en", where, "a", to_whom, self.context
        #print " ".join(self.window_before)
        #print " ".join(self.window)
        #print ""

        get_word = lambda token : token.split("/")[0] if token else ''
        
        who = get_word(who)
        where = get_word(where)
        what = get_word(what)
        to_whom =  get_word(to_whom)
        
        def get_id(ent):
            if ent not in ids_entidades:
                #if ent != '':
                #    print ent
                return ''
            return ids_entidades[ent]

        id_who = get_id(who)
        id_where = get_id(where)
        id_to_whom = get_id(to_whom)

        doc_id = ids_documentos[self.document.replace(".txt", "")]
        
        if args.l:
            #Leíble por humanos:
            return (self.date, self.verb, who, what, where, to_whom, self.document, self.word_count, self.context)
        else:
            #Usar los IDS para poder cargar el modelo relacional
            #Notar que what no tiene id, porque puede ser cualquier cosa, no solo entidades nombradas
            return (self.date, self.verb, id_who, what, id_where, id_to_whom, doc_id, self.word_count, self.context)
            

#Guardar en memoria los Ids de las entidades y de los documentos para su uso posterior
ids_entidades = {}
with open('tablas/entities.csv') as f:
    for line in f:
        line = line.strip()
        id,name,tipo = line.split(",")
        ids_entidades[name.replace(" ","_")] = id

ids_documentos = {}
with open('docs_ruby.tsv') as f:
    for line in f:
        line = line.strip()
        id,name = line.split("\t")
        ids_documentos[name.replace(".txt","").replace("../DOCX/", "")] = id

#Definir e inicializar ciertos parámetros            
corpus_path = "DOCX_txt"
tagged_path = os.path.join(corpus_path, "tagged")
counter = {}
window = 20

candidates = []
entities = []

#Aqui inicia el flujo del programa
for fname in os.listdir(tagged_path):
    fullpath = os.path.join(tagged_path, fname)
    with open(fullpath) as f:
        capturing = False
        current_window = []
        current_sentence = []
        current_window_before = []
        date_in_current_sentence = False
        quoted = []
        capturing_quoted = False
        open_par = False
        prev_tag = False
        word_count = 0
        for line in f:
            line = line.strip()
            values = line.split(" ")
            if len(values) == 4:
                word_count += 1
                word, lemma, tag, prob = values
                
                #No tomar cono Np algunas cosas
                if tag.startswith("NP"):
                    is_np = filter_np(word)
                    if not is_np:
                        tag = "OTHER"
                
                window_word = word+"/"+tag
                current_sentence.append(window_word)
                collapse_cc_np(current_sentence)
                
                #Capturar la fecha de la oración actual
                if tag[0] == "W":
                    date_in_current_sentence = lemma
                    window_word = "FECHA/W"
                    
                #Tomar nota de los paréntesis para saber si algo está dentro de paréntesis    
                if tag == 'Fpa':
                    open_par = True
                elif tag == 'Fpt':
                    open_par = False

                #Capturar lo que esté entre comillas, si no está entre paréntesis
                if capturing_quoted:
                    quoted.append(word)
                if capturing and tag == 'Fra' and not open_par:
                    capturing_quoted = True
                if capturing and tag == 'Frc':
                    capturing_quoted = False

                #Capturar una ventana de lo que está después y antes del verbo
                if word == verbo:
                    current_window.append(word)
                    capturing = True
                elif capturing:
                    current_window.append(window_word)
                    collapse_cc_np(current_window)
                else:
                    current_window_before.append(window_word)
                    collapse_cc_np(current_window_before)
                    if len(current_window_before) == window:
                        current_window_before.pop(0)
                if len(current_window) == window:
                    if date_in_current_sentence and current_window:
                        candidates.append(Candidate(date_in_current_sentence, current_window, current_window_before, current_sentence, quoted, fname, word_count))         
                    current_window = []
                    current_window_before = []
                    capturing = False
                    capturing_quoted = False
                    quoted = []
                prev_tag = tag
            else:
                if date_in_current_sentence and current_window:
                    candidates.append(Candidate(date_in_current_sentence, current_window, current_window_before, current_sentence, quoted, fname, word_count))         
                #Llenar la lista de entidades
                for token in current_sentence:
                    if '/NP' in token:
                        ent = token.split("/")[0]
                        entities.append(ent)
                current_sentence = []
                current_window = []
                current_window_before = []
                capturing = False
                capturing_quoted = False
                quoted = []
                date_in_current_sentence = False

rows = []
for candidate in candidates:
    rows.append(candidate.get_args())

with open("out_" + verbo + ".csv", "wb") as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(rows)
