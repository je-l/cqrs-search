FROM python:3.8-slim-buster

RUN apt-get update && apt-get install --no-install-recommends -y wait-for-it

RUN python3 -m pip install --no-cache-dir pika elasticsearch-dsl watchdog pyyaml argh

ENV PYTHONUNBUFFERED=true
COPY search_import.py /app/

WORKDIR /app

CMD wait-for-it messagequeue-service:5672 -t 120 --strict && wait-for-it searchengine-elasticsearch-service:9200 -t 120 -- watchmedo auto-restart -p "*.py" -R python3 -- search_import.py
