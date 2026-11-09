#!/usr/bin/env python3
"""Reducer: suma el ingreso por producto y emite solo el TOP 10.

Requiere un unico reducer (-D mapreduce.job.reduces=1) para que el top sea global.
Salida:  producto <TAB> ingreso_total (con 2 decimales)
"""
import sys

TOP = 10
totales = {}

for line in sys.stdin:
    try:
        producto, valor = line.rstrip("\n").split("\t")
        totales[producto] = totales.get(producto, 0) + int(valor)
    except ValueError:
        continue

top = sorted(totales.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP]
for producto, centavos in top:
    print(f"{producto}\t{centavos // 100}.{centavos % 100:02d}")
