import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def init():
    """Crea la tabla si no existe (la API espera a que db este lista via healthcheck)."""
    with conn() as c, c.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS resultados (
                   clave TEXT PRIMARY KEY,   -- producto, p. ej. ELE-0001
                   valor NUMERIC(18, 2) NOT NULL  -- ingreso total del anio
               )"""
        )


def fila(k, v):
    return {"clave": k, "valor": float(v)}


@app.get("/")
def raiz():
    return jsonify({"servicio": "DataMart API", "endpoints": ["/resultados", "/resultados/<producto>"]})


@app.get("/resultados")
def todos():
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados ORDER BY valor DESC, clave")
        return jsonify([fila(k, v) for k, v in cur.fetchall()])


@app.get("/resultados/<clave>")
def uno(clave):
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados WHERE clave = %s", (clave,))
        r = cur.fetchone()
    if r is None:
        return jsonify({"error": "no encontrado"}), 404
    return jsonify(fila(*r))


@app.post("/resultados")
def crear():
    d = request.get_json(force=True)
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO resultados (clave, valor) VALUES (%s, %s) "
            "ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor",
            (d["clave"], d["valor"]),
        )
    return jsonify(d), 201


@app.put("/resultados/<clave>")
def actualizar(clave):
    d = request.get_json(force=True)
    with conn() as c, c.cursor() as cur:
        cur.execute("UPDATE resultados SET valor = %s WHERE clave = %s", (d["valor"], clave))
        if cur.rowcount == 0:
            return jsonify({"error": "no encontrado"}), 404
    return jsonify({"clave": clave, "valor": d["valor"]})


@app.delete("/resultados/<clave>")
def borrar(clave):
    with conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM resultados WHERE clave = %s", (clave,))
    return "", 204


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000)
