FROM debian:bookworm-slim

# Java 11 (compatible con Hadoop 3.3), Python 3 y OpenSSH
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless python3 openssh-server openssh-client \
    curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# JAVA_HOME independiente de la arquitectura (amd64/arm64)
RUN ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" /opt/java

ENV JAVA_HOME=/opt/java
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin

# Hadoop en modo standalone (sin configuracion adicional)
RUN curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
      | tar -xz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && echo "export JAVA_HOME=${JAVA_HOME}" >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# Variables disponibles en shells de login y en sesiones SSH
COPY hadoop.sh /etc/profile.d/hadoop.sh
RUN echo "JAVA_HOME=/opt/java" >> /etc/environment \
    && echo "HADOOP_HOME=/opt/hadoop" >> /etc/environment \
    && echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/hadoop/bin" >> /etc/environment

# Usuario sin contrasena ('*' = no hay login por password); solo entra con llave
RUN useradd -m -s /bin/bash hadoop && usermod -p '*' hadoop \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/; s/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
