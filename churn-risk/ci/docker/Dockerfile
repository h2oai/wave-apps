#ARG WAVE_IMAGE
#FROM ${WAVE_IMAGE}
FROM golang:1.13
ENV DEBIAN_FRONTEND=noninteractive

ARG uid
ARG gid

#ENV FLASK_APP=app.py
#ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get -q -y update
RUN apt-get install -y openjdk-11-jre
#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt
#EXPOSE 5000
#COPY . .
#CMD ["flask", "run"]

WORKDIR /app