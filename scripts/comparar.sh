#!/bin/bash
# Mide MapReduce vs secuencial y verifica que los resultados coincidan.
#   docker compose exec -u hadoop hadoop bash /scripts/comparar.sh 125052336
MAT="${1:-125052336}"
IN="/data/input/ventas_${MAT}.csv"
TIMEFORMAT='tiempo real: %R s'

echo ">>> Hadoop Streaming"
time bash /scripts/run_job.sh "$MAT" > /tmp/job.log 2>&1 || { tail -30 /tmp/job.log; exit 1; }
cp /data/output/resultado/part-00000 /tmp/mr.txt

echo ">>> Secuencial"
time python3 /home/hadoop/mapreduce/secuencial.py "$IN" > /tmp/seq.txt

if diff <(sort /tmp/mr.txt) <(sort /tmp/seq.txt) > /dev/null; then
  echo "RESULTADOS COINCIDEN"
else
  echo "LOS RESULTADOS NO COINCIDEN"; diff <(sort /tmp/mr.txt) <(sort /tmp/seq.txt)
fi
