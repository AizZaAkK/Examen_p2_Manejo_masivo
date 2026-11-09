#!/usr/bin/env python3
"""Lee la salida del job (part-00000) e inserta los registros en PostgreSQL.

Uso (dentro del contenedor api):
    python /scripts/cargar_resultados.py [ruta_part-00000]
Es idempotente: vacia la tabla antes de insertar.
"""
import os
import sys

import psycopg2

ruta = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"

c = psycopg2.connect(
    host=os.environ.get("DB_HOST", "db"),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

n = 0
with c, c.cursor() as cur, open(ruta) as f:
    cur.execute(
        """CREATE TABLE IF NOT EXISTS resultados (
               clave TEXT PRIMARY KEY,
               valor NUMERIC(18, 2) NOT NULL
           )"""
    )
    cur.execute("TRUNCATE resultados")
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        clave, valor = line.split("\t")
        cur.execute("INSERT INTO resultados (clave, valor) VALUES (%s, %s)", (clave, valor))
        n += 1
print(f"{n} registros cargados desde {ruta}")
