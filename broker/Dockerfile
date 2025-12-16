FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnuradio \
    python3 \
    python3-pip \
    libzmq3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY broker/gnu_radio_broker_script.py /app/gnu_radio_broker_script.py
COPY broker/config.json /app/config.json

ENTRYPOINT ["/usr/bin/python3", "/app/gnu_radio_broker_script.py"]
