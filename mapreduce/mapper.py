#!/usr/bin/env python3
"""Mapper: emite  producto <TAB> ingreso_en_centavos  para cada venta.

Pregunta (matricula terminada en 6): Top 10 productos por ingreso total del anio.
Se trabaja en centavos (enteros) para que la suma sea exacta y coincida con secuencial.py.
"""
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("id,"):      # ignora lineas vacias y el encabezado
        continue
    try:
        p = line.split(",")
        if len(p) != 8:                         # linea mal formada: se omite
            continue
        producto = p[4]
        cantidad = int(p[5])
        precio_centavos = round(float(p[6]) * 100)
        if not producto:
            continue
        print(f"{producto}\t{cantidad * precio_centavos}")
    except (ValueError, IndexError):
        continue                                # no truncar el job por una linea mala
