FROM python:3.9-stretch

ENV PYTHONUNBUFFERED 1

# Copy over the RDS Certificate Authority Bundle
# See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html
COPY ds-ca-2019-root.pem /ds-ca-2019-root.pem

# Copy over chamber, which is used for reading secrets in AWS SSM Parameter Store
# See https://github.com/segmentio/chamber
COPY bin_linux/chamber /bin/chamber

RUN mkdir /kanga

WORKDIR /kanga

COPY requirements.txt /kanga/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /kanga/
