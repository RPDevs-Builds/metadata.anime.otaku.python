import os
import time
import json
import xbmcaddon
import xbmcvfs
from sqlite3 import dbapi2 as sqlite

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
DB_FILE = os.path.join(PROFILE_PATH, 'cache.db')

def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

class SQL:
    def __init__(self, path=DB_FILE, timeout=30):
        self.path = path
        self.timeout = timeout

    def __enter__(self):
        if not xbmcvfs.exists(PROFILE_PATH):
            xbmcvfs.mkdirs(PROFILE_PATH)
        try:
            self._conn = sqlite.connect(self.path, timeout=self.timeout, isolation_level=None)
            self._conn.row_factory = _dict_factory
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA synchronous = OFF")
            self._conn.execute("PRAGMA journal_mode = WAL")
            self._cursor = self._conn.cursor()
            return self._cursor
        except Exception as e:
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._cursor is not None:
                self._cursor.close()
            if self._conn is not None:
                self._conn.close()
        except Exception:
            pass

def get_cache(key):
    with SQL() as cur:
        cur.execute('SELECT value, expiry FROM cache WHERE key=?', (key,))
        row = cur.fetchone()
        if row:
            if row['expiry'] > int(time.time()) or row['expiry'] == 0:
                return json.loads(row['value'])
            else:
                cur.execute('DELETE FROM cache WHERE key=?', (key,))
                cur.connection.commit()
    return None

def set_cache(key, value, expiry_hours=24):
    expiry = int(time.time() + (expiry_hours * 3600)) if expiry_hours > 0 else 0
    with SQL() as cur:
        cur.execute(
            'REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)',
            (key, json.dumps(value), expiry)
        )
        cur.connection.commit()
