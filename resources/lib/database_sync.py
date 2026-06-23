from .database import SQL

class SyncDatabase:
    SCHEMA_VERSION = '1.0.0'

    def __init__(self):
        self._create_tables()

    def _create_tables(self):
        with SQL() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expiry INTEGER
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS episodes_meta (
                    mal_id INTEGER,
                    tvdb_id INTEGER,
                    episode INTEGER,
                    data TEXT,
                    PRIMARY KEY (mal_id, episode)
                )
            ''')
            cur.connection.commit()

# Run this on scraper startup
def init_db():
    SyncDatabase()
