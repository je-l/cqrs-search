from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def main():
    """TODO: Implement endpoint which can be used to add more music data.

    Currently we have the seed_database.py script.
    """
    return {"works": "yes"}
