FROM nginx:stable
LABEL org.opencontainers.image.authors="code@dds.mil"

COPY conf/default.conf /etc/nginx/conf.d/default.conf

RUN apt-get update && \
  rm -rf /var/lib/apt/lists/*
