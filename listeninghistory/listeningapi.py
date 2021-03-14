from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import pika
import json

app = FastAPI()

pika_conn = pika.BlockingConnection(
    pika.ConnectionParameters('messagequeue-service')
)
channel = pika_conn.channel()
4
conn = psycopg2.connect(
    "user=postgres host=listeninghistory-database-service password=1234"
)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute('DROP TABLE IF EXISTS listens')
cur.execute(
    '''
    CREATE TABLE listens (
        id SERIAL,
        user_id TEXT NOT NULL,
        release_id TEXT NOT NULL,
        listen_count INT NOT NULL DEFAULT 1,
        UNIQUE (release_id, user_id)
    )
    '''
)
conn.commit()


class Listen(BaseModel):
    release_id: str
    user_id: str


@app.post('/listen')
def add_listen(listen: Listen):
    cur.execute(
        '''INSERT INTO listens (
            release_id,
            user_id
        ) VALUES (
            %(release_id)s,
            %(user_id)s
        )
        ON CONFLICT (release_id, user_id)
        DO UPDATE SET listen_count = listens.listen_count + 1
        RETURNING id
        ''',
        listen.dict(),
    )
    inserted_id = cur.fetchone()
    cur.execute(
        '''
        SELECT * FROM listens WHERE id = %(id)s
    ''',
        inserted_id,
    )
    conn.commit()
    inserted = cur.fetchone()
    channel.basic_publish(
        exchange='', routing_key='listen_event', body=json.dumps(inserted)
    )
    return inserted
