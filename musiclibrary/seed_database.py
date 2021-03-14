from glob import glob
from dataclasses import dataclass
import gzip
import xmltodict
import json
import psycopg2
import psycopg2.extras
import pika

# Instead of importing the full Discogs dataset, only import a subset
IMPORT_LIMIT = 500_000

BATCH_SIZE = 1000

DISCOGS_GLOB = '/discogs/discogs_*_releases.xml.gz'

conn = psycopg2.connect(
    "user=postgres host=musiclibrary-database-service password=1234"
)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute('CREATE TABLE IF NOT EXISTS releases (id SERIAL, title TEXT)')
cur.execute('DELETE FROM releases')
conn.commit()

rabbitmq_conn = pika.BlockingConnection(
    pika.ConnectionParameters('messagequeue-service')
)
channel = rabbitmq_conn.channel()


@dataclass
class DiscogsReleaseWriter:
    rows_inserted: int = 0
    insert_batch = []

    def write_release(self, _, row):
        self.insert_batch.append({"title": row['title']})
        self.rows_inserted += 1
        if (self.rows_inserted % BATCH_SIZE) == 0:
            cur.executemany(
                'INSERT INTO releases (title) VALUES (%(title)s) RETURNING id',
                self.insert_batch,
            )
            cur.execute(
                'SELECT * FROM releases ORDER BY id DESC LIMIT %(batch)s',
                {"batch": BATCH_SIZE},
            )
            inserted = cur.fetchall()
            conn.commit()
            self.insert_batch = []
            channel.basic_publish(
                exchange='',
                routing_key='new_releases',
                body=json.dumps(inserted),
            )
            print(f'published a batch of {BATCH_SIZE} release create events')
            if self.rows_inserted >= IMPORT_LIMIT:
                return False

        return True


def run() -> None:
    print('starting Discogs import...')

    channel.queue_declare(queue='new_releases')
    try:
        discogs_file_name = glob(DISCOGS_GLOB)[0]
    except IndexError:
        print('No discogs dataset found. Please see README.')
    else:
        print('starting to import discogs data...')
        try:
            xmltodict.parse(
                gzip.GzipFile(discogs_file_name),
                item_depth=2,
                item_callback=DiscogsReleaseWriter().write_release,
            )
        except xmltodict.ParsingInterrupted:
            print('done')


if __name__ == '__main__':
    run()
