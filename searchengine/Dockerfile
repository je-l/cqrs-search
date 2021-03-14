FROM python:3.8-slim-buster

RUN python3 -m pip install --no-cache-dir fastapi==0.63.0 uvicorn elasticsearch-dsl==7.3.0

COPY searchapi.py /app/

WORKDIR /app

CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "searchapi:app"]
