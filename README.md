# CQRS study project

### Running the project

1. Install skaffold and minikube
1. clone the project
1. Download [Discogs *releases.xml.gz](https://data.discogs.com/) dataset (8.8GB) into ./discogs/ directory
1. Start minikube with `minikube start --mount-string="$(pwd)/discogs:/discogs" --mount`
1. Run `skaffold dev --port-forward`

Clear elasticsearch: `curl -X DELETE localhost:9200/release`

Import test data into Music library service: `kubectl exec -it deployment musiclibrary -- python3 seed_database.py`

Add track listen event: `curl --data '{"release_id": "145048", "user_id": "123"}' localhost:5000/listen `

Test the search API with `curl 'localhost:7000/search?term=he&user_id=123`
