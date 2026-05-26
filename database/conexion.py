# db.py

from pymongo import MongoClient

_client = None
_db = None

def get_db():
    """
    Retorna la conexión única a MongoDB.
    """
    global _client, _db
    if _db is None:
        _client = MongoClient(
            "mongodb://localhost:27017/"
        )
        _db = _client["zapateria_pmv"]
    return _db