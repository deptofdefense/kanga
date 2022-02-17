FROM postgres:14
MAINTAINER Defense Digital Service <code@dds.mil>

RUN apt-get update && \
apt-get install -y postgis postgresql-14-postgis-3-scripts && \
rm -rf /var/lib/apt/lists/*
