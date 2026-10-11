from functools import lru_cache
from google.cloud.firestore import AsyncClient


@lru_cache
def get_db():
    """
    Return de database connections
    :return: database connection
    """
    return AsyncClient()
