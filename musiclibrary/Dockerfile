FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y git libpq5
RUN python3 -m pip install fastapi==0.63.0 uvicorn xmltodict psycopg2-binary pika

COPY *.py /app/

WORKDIR /app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--reload"]
