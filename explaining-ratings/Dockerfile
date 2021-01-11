FROM python:3.7-buster
WORKDIR /app
COPY ./src /app/src
COPY ./static /app/static
COPY ./data /app/data
COPY ./requirements.txt /app/
COPY Makefile /app/
RUN make setup

RUN wget https://github.com/h2oai/wave/releases/download/v0.10.0/wave-0.10.0-linux-amd64.tar.gz
RUN tar xf wave-0.10.0-linux-amd64.tar.gz

WORKDIR wave-0.10.0-linux-amd64
COPY ./script.sh .
RUN chmod +x script.sh
EXPOSE 10101 8000
ENTRYPOINT ["/app/wave-0.10.0-linux-amd64/script.sh"]