# -*- coding: utf-8 -*-
import sys
import os
import re
import csv

corpus_path = "DOCX_txt"
tagged_path = os.path.join(corpus_path, "tagged")
entities = []

def collapse_cc_np(stack):
    """
        Recibe una lista de tokens de la forma palabra/tag y tranforma la secuencia
        /NP /CC /NP
        en /NP
        por ejemplo para transformar Secretaría_de_Comuincaciones/NP y/CC Transportes/NP en una sola entidad
    """
    if stack and not '/NP' in stack[-1]:
        return
    if len(stack) >= 3:
        np2 = stack[-1]
        cc = stack[-2]
        np = stack[-3]
        if cc == 'y/CC' and '/NP' in np:
            word1 = np.split("/")[0]
            word2 = cc.split("/")[0]
            word3,tag = np2.split("/")
            new_ne = word1 + "_" + word2 + "_" + word3 + "/" + tag
            stack.pop()
            stack.pop()
            stack.pop()
            stack.append(new_ne)

def filter_np(entity):
    """
        Recibe un candidato a entidad (NP de Freeling), y decide si sí es una entidad o no.

        Retorna:
            True si es entidad
            False si no es
    """
    for char in entity:
        if not char.isupper():
            all_upper = False
    else:
        all_upper = True
    if len(entity) > 70:
        return False
    if len(entity) < 4 and not all_upper:
        return False
    if "REPRESENTADA_EN" in entity or "EN_LO_SUCESIVO" in entity or  "MEDIANTE_EL_CUAL" in entity or 'MEDIANTE_LA_CUAL' in entity or 'POR_EL_CUAL' in entity or 'POR_LA_CUAL' in entity:
        return False
    first = entity.split("_")[0]
    all = entity.split("_")
    if first.count(".") >= 2:
        return False
    if first.lower() in ['fracción','de','a','para','por']:
        return False
    if re.match("[.)ABCIVXCDLM]+$", first):
        if not (len(all) >= 2 and first == 'C.'):
            return False
    ordinales = ["Primero","Segundo","Tercero","Cuarto","Quinto","Sexto","Séptimo","Octavo","Noveno","Décimo"]
    for ordinal in ordinales:
        if first.lower().startswith(ordinal.lower()):
            return False
    return True

for fname in os.listdir(tagged_path):
    print fname
    fullpath = os.path.join(tagged_path, fname)
    print fullpath
    with open(fullpath) as f:
        capturing = False
        current_sentence = []
        for line in f:
            line = line.strip()
            values = line.split(" ")
            if len(values) == 4:
                word, lemma, tag, prob = values

                #No tomar cono Np algunas cosas
                if tag.startswith("NP"):
                    is_np = filter_np(word)
                    if not is_np:
                        tag = "OTHER"

                window_word = word+"/"+tag
                current_sentence.append(window_word)
                collapse_cc_np(current_sentence)

            else:
                for token in current_sentence:
                    if '/NP' in token:
                        ent = token.split("/")[0]
                        entities.append(ent)
                current_sentence = []

with open("out_entities", "w") as f:
    for ent in entities:
        f.write(ent+"\n")
