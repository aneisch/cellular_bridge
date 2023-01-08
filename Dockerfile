FROM python:3-alpine

ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY cellular_bridge.py /

EXPOSE 11111

ENV LISTEN_PORT 11111
ENV LISTEN_IP 0.0.0.0
ENV PUSHOVER_TOKEN xxxxx
ENV PUSHOVER_USER xxxxx
ENV SIM_KEY xxxxx

RUN adduser -D cellular_bridge
RUN chmod 777 /cellular_bridge.py

USER cellular_bridge

ENTRYPOINT python -u /cellular_bridge.py
