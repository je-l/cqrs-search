FROM python:3.8-slim-buster

RUN apt-get update && apt-get install --no-install-recommends -y wait-for-it

RUN pip3 install --no-cache-dir fastapi==0.63.0 uvicorn psycopg2-binary pika

COPY listeningapi.py /app/

WORKDIR /app

CMD wait-for-it -t 120 messagequeue-service:5672 -- uvicorn --reload listeningapi:app
