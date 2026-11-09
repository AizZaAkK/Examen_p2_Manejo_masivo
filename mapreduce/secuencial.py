#!/usr/bin/env python3
"""Version secuencial (linea a linea) de la misma pregunta: Top 10 productos por ingreso."""
import csv
import sys
from collections import defaultdict

ruta = sys.argv[1]
totales = defaultdict(int)

with open(ruta, newline="") as f:
    lector = csv.reader(f)
    next(lector, None)                          # encabezado
    for p in lector:
        try:
            if len(p) != 8:
                continue
            totales[p[4]] += int(p[5]) * round(float(p[6]) * 100)
        except (ValueError, IndexError):
            continue

top = sorted(totales.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
for producto, centavos in top:
    print(f"{producto}\t{centavos // 100}.{centavos % 100:02d}")
