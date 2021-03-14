from fastapi import FastAPI
from elasticsearch_dsl import (
    Document,
    SearchAsYouType,
    connections,
    Text,
    Object,
)
from elasticsearch_dsl.query import MultiMatch, FunctionScore
from elasticsearch_dsl.function import FieldValueFactor

app = FastAPI()

connections.create_connection(hosts=['searchengine-elasticsearch-service'])


class Release(Document):
    title = SearchAsYouType
    id = Text()
    user_listens = Object()

    class Index:
        name = 'release'


@app.get('/search')
def search_releases(term: str, user_id: str):
    """Search music releases with priority for previously listened tracks."""
    search = Release.search()
    search.query = FunctionScore(
        query=MultiMatch(
            query=term,
            type="bool_prefix",
            fields=["title", "title._2gram", "title._3gram"],
        ),
        functions=[
            # Weight results with higher listen count
            FieldValueFactor(field=f'user_listens.{user_id}', missing=0,)
        ],
    )

    response = search.execute()

    return [
        {
            "id": release.id,
            "title": release.title,
            "listens": release.user_listens.to_dict().get(user_id, 0),
        }
        for release in response
    ]
