ARG WAVE_IMAGE
FROM ${WAVE_IMAGE}

ARG uid

USER root

RUN apt-get -q -y update
RUN apt-get install -q -y openjdk-11-jre

USER ${uid}

WORKDIR /app
