# Examen Segundo Parcial — Pipeline de datos contenedorizado

- **Alumno / matrícula:** 125052336
- **Materia:** Manejo Masivo de Datos (Big Data), UPQ
- **Pregunta asignada (último dígito 6):** Top 10 productos por ingreso total (`cantidad × precio_unitario`) en todo el año.

## Cómo levantar el ambiente

```bash
# 1) Dataset (NO se sube al repo; queda en data/ y se monta de solo lectura)
python3 scripts/generar_dataset.py 125052336
mv ventas_125052336.csv data/

# 2) Variables de entorno
cp .env.example .env        # edita la contraseña si quieres

# 3) Todo el ambiente con un solo comando
docker compose up --build -d
```

## Pasos para reproducir las evidencias

```bash
# A1: hadoop version
docker compose exec -u hadoop hadoop hadoop version

# B: SSH sin contraseña
docker compose exec -u hadoop hadoop ssh localhost 'echo OK desde $(hostname)'
docker compose exec api ssh hadoop 'echo OK desde $(hostname)'

# C: job de Hadoop Streaming + comparativa contra secuencial
docker compose exec -u hadoop hadoop bash /scripts/comparar.sh 125052336

# D: carga a PostgreSQL y consultas a la API
docker compose exec api python /scripts/cargar_resultados.py
curl localhost:5000/resultados
curl localhost:5000/resultados/PAP-0013        # usa un producto de tu top
curl -X POST localhost:5000/resultados -H "Content-Type: application/json" -d '{"clave":"PRUEBA","valor":1}'
curl -X DELETE localhost:5000/resultados/PRUEBA

# Persistencia
docker compose down && docker compose up -d
curl localhost:5000/resultados                 # los datos siguen ahí
```

Las capturas van en `evidencias/` (`hadoop version`, `ssh`, salida del job, respuesta de la API, persistencia).

## Arquitectura

- `hadoop`: Debian + OpenJDK 11 + Python 3 + Hadoop 3.3.6 standalone + OpenSSH. Las llaves SSH se generan al arrancar y viven en un volumen (no en el repo).
- `db`: PostgreSQL 16, volumen nombrado `pgdata`, credenciales en `.env`.
- `api`: Flask; se conecta a `db` por nombre de servicio. `depends_on` hacia `db` (con healthcheck).
- Los tres servicios comparten la red `datamart`.

## Comparativa de rendimiento (C2)

| Método | Tiempo | Resultado |
|---|---|---|
| Hadoop Streaming (standalone) | _completar_ | _coincide / no_ |
| Script secuencial Python | _completar_ | _coincide / no_ |

_Completar con la salida de `comparar.sh`. Párrafo (ajústalo a tus tiempos reales):_ En modo standalone Hadoop corre en un solo nodo y no hay paralelismo real entre máquinas. A eso se suma el arranque de la JVM, el coste de comunicar cada línea por pipes con los procesos Python de Streaming y las fases de ordenamiento y shuffle. Con 400 MB, que caben sin problema en un solo equipo, el script secuencial no paga ese overhead y termina antes. MapReduce conviene cuando los datos son de decenas o cientos de GB y se reparten entre varios nodos.

## Parte E. Teoría

1. **Modos de Hadoop.** *Standalone:* un solo proceso Java, sin demonios, usando el sistema de archivos local (no hay HDFS). *Pseudo-distribuido:* todos los demonios (NameNode, DataNode, ResourceManager…) en una sola máquina, cada uno en su proceso; **aquí se usa HDFS** y por eso necesita SSH sin contraseña. *Totalmente distribuido:* los demonios se reparten en un clúster de varias máquinas, con HDFS replicado entre nodos.
2. **Dataset como volumen y no `COPY`.** (a) La imagen no crece 400 MB, así que se construye y se comparte más rápido. (b) Se puede cambiar o regenerar el dataset sin reconstruir la imagen. (c) Los datos quedan fuera de las capas de la imagen y del repo. (d) Se monta en solo lectura (`:ro`), así el contenedor no lo puede alterar.
3. **`down` vs `down -v`.** `docker compose down` elimina contenedores y redes, pero **conserva** los volúmenes nombrados, por lo que los datos de la base siguen ahí al volver a hacer `up`. `docker compose down -v` también elimina los volúmenes, así que **se pierde** la base de datos y hay que recargar los resultados.
4. **MapReduce vs secuencial en 400 MB.** Hay overhead fijo (arranque de JVM, planificación de tareas, serialización por pipes, ordenamiento/shuffle) y en un solo nodo no hay paralelismo real. Para 400 MB un bucle secuencial lee el archivo una vez y termina antes. MapReduce conviene cuando el volumen es de decenas o cientos de GB, cuando no cabe en memoria o en un disco, o cuando hay un clúster con varios nodos para repartir el trabajo.
5. **`CMD` vs `ENTRYPOINT`; `COPY` vs `ADD`.** `ENTRYPOINT` define el ejecutable fijo del contenedor y `CMD` sus argumentos por defecto, que se pueden sobrescribir al hacer `docker run`. `COPY` solo copia archivos o carpetas del contexto de build; `ADD` hace lo mismo pero además descomprime archivos tar locales y acepta URLs, por eso se prefiere `COPY` salvo que se necesite eso.
