# -*- coding: utf-8 -*-
#------------------------------------------------------
# Script para convertir los archivos DOCX a txt
#------------------------------------------------------
# No recibe argumentos.
# Los archivos los busca en una carpeta llamada DOCX y pone los convertidos en una llamada DOCX_txt.
# Puede realizar preprocesamientos adicionales para mejorar la precisión de freeling
#------------------------------------------------------
import docx2txt
import os
import sys
path_docx = "DOCX"
path_txt = path_docx.strip("/") + "_txt"
if not os.path.isdir(path_txt):
    os.makedirs(path_txt)
for fname in os.listdir(path_docx):
    fullpath = os.path.join(path_docx, fname)
    text = docx2txt.process(fullpath)
    text = text.replace("Con cesiones", "Concesiones")
    text = text.replace("y Transportes", "Y_Transportes")
    text = text.replace("y Concesiones", "Y_Concesiones")
    text = text.replace("y Servicios", "Y_Servicios")
    text = text.replace("  ", " ")
    text = text.replace(", S.A. de C.V.", " Sadecv")
    text = text.replace(", S.A.B. de C.V.", " Sabdecv")
    text = text.replace(", S.R.L. de C.V.", " Srlecv")
    text = text.replace(", S. de R.L. de C.V.", " Srldecv")
    text = text.replace(", S. de R.L.", " Srldecv")
    text = text.replace(", S.A.P.I. de C.V.", " Sapidecv")
    text = text.replace("S.A. de C.V.", " Sadecv")
    text = text.replace("S.A.B. de C.V.", " Sabdecv")
    text = text.replace("S.R.L. de C.V.", " Srlecv")
    text = text.replace("S. de R.L. de C.V.", " Srldecv")
    text = text.replace("S. de R.L.", " Srlecv")
    text = text.replace("S.A.P.I. de C.V.", " Sapidecv")
    text = text.replace("S.A. DE C.V.", " SADECV")
    text = text.replace("S.A.B. DE C.V.", " SABDECV")
    text = text.replace("S.R.L. DE C.V.", " SRLDECV")
    text = text.replace("S. DE R.L. DE C.V.", " SRLDECV")
    text = text.replace("S. DE R.L.", " SRLDECV")
    text = text.replace("S.A.P.I. DE C.V.", " SAPIDECV")
    fullpath_output = os.path.join(path_txt, fname + ".txt")
    with open(fullpath_output, "w") as f:
        f.write(text.encode("utf-8"))
