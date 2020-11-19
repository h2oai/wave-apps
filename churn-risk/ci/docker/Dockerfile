ARG WAVE_IMAGE
FROM ${WAVE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive

#ARG uid
#ARG gid
USER root
RUN apt-get -q -y update
RUN apt-get install -y openjdk-11-jre
USER uid
WORKDIR /app



#ENV FLASK_APP=app.py
#ENV FLASK_RUN_HOST=0.0.0.0

#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt
#EXPOSE 5000
#COPY . .
#CMD ["flask", "run"]

