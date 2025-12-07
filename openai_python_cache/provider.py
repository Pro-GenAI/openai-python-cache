import hashlib
import json
from typing import TypedDict, Optional

import sqlite3


class CacheSettings(TypedDict):
    db_loc: str


DEFAULT_CACHE_SETTINGS: CacheSettings = {
    "db_loc": "./openai_cache.db",
}


class Sqlite3CacheProvider(object):
    CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS cache(
            key string PRIMARY KEY NOT NULL,
            request_params json NOT NULL,
            response string NOT NULL
        );
    """

    def __init__(self, settings: CacheSettings = DEFAULT_CACHE_SETTINGS):
        self.conn: sqlite3.Connection = sqlite3.connect(settings.get("db_loc"))
        self.create_table_if_not_exists()

    def get_curr(self) -> sqlite3.Cursor:
        return self.conn.cursor()

    def create_table_if_not_exists(self):
        self.get_curr().execute(self.CREATE_TABLE)

    def hash_params(self, params: dict):
        stringified = json.dumps(params).encode("utf-8")
        hashed = hashlib.md5(stringified).hexdigest()
        return hashed

    def get_response(self, key: str) -> Optional[str]:
        res = (
            self.get_curr()
            .execute("SELECT * FROM cache WHERE key= ?", (key,))
            .fetchone()
        )
        if not res:
            return None
        return res[-1]

    def insert(self, key: str, request: dict, response: str):
        self.get_curr().execute(
            "INSERT INTO cache VALUES (?, ?, ?)",
            (
                key,
                json.dumps(request),
                response,
            ),
        )
        self.conn.commit()


# Test storing json and retrieving, and check data type after fetching
if __name__ == "__main__":
    import random

    provider = Sqlite3CacheProvider()
    test_key = "test_key" + str(random.randint(1, 1000))
    test_request = {"param1": "value1", "param2": 2}
    test_response = "This is a test response."

    provider.insert(test_key, test_request, test_response)
    cached_response = provider.get_response(test_key)
    print(f"Type of cached response: {type(cached_response)}")
    print(f"Cached response: {cached_response}")
