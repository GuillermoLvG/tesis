#!/bin/bash
# Script para obtener eventos de varios verbos y concatenarlos todos en el mismo CSV
for verb in solicitó otorgó emitió publicó presentó
do
    echo "Obteniendo eventos para $verb"
    python eventos.py $verb
done
cat out_*.csv > events.csv
rm out_*.csv
