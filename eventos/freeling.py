# -*- coding: utf-8 -*-
#---------------------------------------------------
# Script para procesar con Freeling los documentos
#---------------------------------------------------
# No recibe argumentos, busca los archivos a convertir en la carpeta DOCX_txt y os pone en DOC_txt/tagged.
# Usa el servicio freeling web que está en el servidor del GIL
#---------------------------------------------------
import os
import sys
import requests

global path_corpus
global path_tagged

def get_dir(suffix, delete=True):
    new_dir = os.path.join(path_corpus, suffix)
    if os.path.isdir(new_dir) and delete:
        os.system("rm -r %s"%new_dir)
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    return new_dir

def freeling(language):
    for fname in os.listdir(path_corpus):
        full_path = os.path.join(path_corpus, fname)
        if not os.path.isfile(full_path):
            continue
        full_path_tagged = os.path.join(path_corpus_tagged, fname)
        print (full_path)
      
        files = {'file': open(full_path, 'rb')}
        params = {'outf': 'tagged'+language, 'format': 'plain'}
        url = "http://www.corpus.unam.mx/servicio-freeling/analyze.php"
        r = requests.post(url, files=files, params=params, stream=True)
        r.encoding= 'utf-8'
        text = r.content
        with open(full_path_tagged, "wb") as f:
            f.write(text)

if __name__ == "__main__":
    global path_corpus, path_tagged
    path_corpus = "DOCX_txt"
    if len(sys.argv) == 3:
        language = "_" + sys.argv[2]
    else:
        language = ""
    path_corpus_tagged = get_dir("tagged", delete=True)
    freeling(language)
    
