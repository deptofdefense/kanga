FROM python:3.9-buster

ENV PYTHONUNBUFFERED 1

env KANGA_VERSION 0.0.1

# Copy over the RDS Certificate Authority Bundle
# See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html
COPY temp/rds-ca-2019-root.pem /rds-ca-2019-root.pem

# Copy over chamber, which is used for reading secrets in AWS SSM Parameter Store
# See https://github.com/segmentio/chamber
COPY bin_linux/chamber /bin/chamber

RUN mkdir /kanga

WORKDIR /kanga

RUN pwd && ls -la

COPY temp/requirements.txt /kanga/

COPY temp/kanga-${KANGA_VERSION}-py3-none-any.whl /kanga

RUN pwd && ls -la

RUN pip --no-cache-dir install gunicorn==20.1.0 gevent==21.8.0

RUN pip --no-cache-dir install -r /kanga/requirements.txt \
&& rm -f /kanga/requirements.txt

RUN pip --no-cache-dir install --no-dependencies file:///kanga/kanga-${KANGA_VERSION}-py3-none-any.whl \
&& rm -f /kanga/kanga-${KANGA_VERSION}-py3-none-any.whl

COPY gunicorn.conf.py /

COPY entrypoint.sh /

COPY . /kanga/

# ENTRYPOINT [ /bin/bash entrypoint.sh ]
