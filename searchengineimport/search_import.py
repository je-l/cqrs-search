import json
import pika
from elasticsearch_dsl import (
    Document,
    SearchAsYouType,
    connections,
    Text,
    Object,
    Search,
)
from elasticsearch.helpers import bulk


class Release(Document):
    title = SearchAsYouType
    id = Text()
    user_listens = Object()

    class Index:
        name = 'release'


class Listen(Document):
    release_id = Text
    user_id = Text

    class Index:
        name = 'listen'


def new_release_callback(ch, method, properties, body):
    parsed = json.loads(body.decode('utf8'))
    releases = [Release(**r).to_dict(include_meta=True) for r in parsed]
    bulk(connections.get_connection(), releases)
    print(f'wrote {len(releases)} items to elasticsearch')


def new_listen_callback(ch, method, properties, body):
    parsed_body = body.decode('utf8')
    listen = json.loads(parsed_body)
    response = (
        Search(index='release')
        .query('match', id=listen['release_id'])
        .execute()
    )
    found_doc = next((i for i in response), None)

    if found_doc:
        doc = Release.get(found_doc.meta.id)
        listens = doc.user_listens.to_dict()
        listens[listen['user_id']] = listens.get(listen['user_id'], 0) + 1
        doc.update(user_listens=listens)
        print('added new listen to', listen)
    else:
        print(f'no doc found for release_id {listen["release_id"]}')


def run():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('messagequeue-service', 5672)
    )
    channel = connection.channel()
    channel.queue_declare(queue='new_releases')
    channel.queue_declare(queue='listen_event')
    channel.basic_consume(
        queue='new_releases',
        auto_ack=True,
        on_message_callback=new_release_callback,
    )
    channel.basic_consume(
        queue='listen_event',
        auto_ack=True,
        on_message_callback=new_listen_callback,
    )
    print('listening to channels...')
    channel.start_consuming()


if __name__ == '__main__':
    connections.create_connection(hosts=['searchengine-elasticsearch-service'])
    Release.init()
    Listen.init()
    run()
