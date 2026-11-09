#!/bin/sh
# Espera la llave que genera el contenedor hadoop y la instala para ssh hadoop@hadoop
for i in $(seq 1 60); do
  [ -f /keys/id_ed25519 ] && break
  sleep 1
done

mkdir -p ~/.ssh
if [ -f /keys/id_ed25519 ]; then
  cp /keys/id_ed25519 ~/.ssh/id_ed25519
  chmod 600 ~/.ssh/id_ed25519
  printf 'Host hadoop\n  User hadoop\n  IdentityFile ~/.ssh/id_ed25519\n  StrictHostKeyChecking accept-new\n' > ~/.ssh/config
fi

exec python app.py
