#!/bin/bash
# Ejecuta el job de Hadoop Streaming. Correr dentro del contenedor hadoop:
#   docker compose exec -u hadoop hadoop bash /scripts/run_job.sh 125052336
set -e
source /etc/profile.d/hadoop.sh

MAT="${1:-125052336}"
IN="/data/input/ventas_${MAT}.csv"
OUT="/data/output/resultado"

# Hadoop Streaming escribe en el directorio actual (desempaqueta su jar),
# y /home/hadoop/mapreduce esta montado como solo lectura: se trabaja en una copia.
WORK="$(mktemp -d)"
cp /home/hadoop/mapreduce/mapper.py /home/hadoop/mapreduce/reducer.py "$WORK"/
cd "$WORK"

rm -rf "$OUT"          # Hadoop exige que el directorio de salida NO exista

hadoop jar "$HADOOP_HOME"/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -D mapreduce.job.reduces=1 \
  -input "$IN" \
  -output "$OUT" \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -file mapper.py -file reducer.py

echo "=== Resultado (Top 10) ==="
cat "$OUT"/part-00000
