#!/bin/bash
set -e
mkdir -p /run/sshd /keys /data/output

# Par de llaves generado al arrancar, guardado en el volumen "sshkeys".
# Asi no hay llaves ni contrasenas dentro del repo ni de la imagen.
if [ ! -f /keys/id_ed25519 ]; then
  ssh-keygen -t ed25519 -N "" -C hadoop@examen -f /keys/id_ed25519
fi

install -d -m 700 -o hadoop -g hadoop /home/hadoop/.ssh
cp /keys/id_ed25519 /keys/id_ed25519.pub /home/hadoop/.ssh/
cp /keys/id_ed25519.pub /home/hadoop/.ssh/authorized_keys
printf 'Host *\n  StrictHostKeyChecking accept-new\n' > /home/hadoop/.ssh/config
chown -R hadoop:hadoop /home/hadoop/.ssh
chmod 600 /home/hadoop/.ssh/id_ed25519 /home/hadoop/.ssh/authorized_keys /home/hadoop/.ssh/config

# El contenedor api copia la llave desde este volumen interno de Docker
chmod 644 /keys/id_ed25519 /keys/id_ed25519.pub

# El usuario hadoop debe poder escribir la salida del job
chown hadoop:hadoop /data/output

exec /usr/sbin/sshd -D -e
