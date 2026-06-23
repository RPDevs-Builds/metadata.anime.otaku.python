import sqlite3
import json
import os

cache_db_path = os.path.expanduser('~/.var/app/tv.kodi.Kodi/data/userdata/addon_data/metadata.anime.otaku.python/cache.db')
log_path = os.path.expanduser('~/.var/app/tv.kodi.Kodi/data/temp/kodi.log')

# Check Cache Data
print("--- CACHE DATA ---")
try:
    conn = sqlite3.connect(f"file:{cache_db_path}?mode=ro", uri=True)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM cache WHERE key='episode_meta_40832'")
    row = cursor.fetchone()
    if row:
        data = json.loads(row[0])
        print(f"Episodes in cache: {len(data)}")
        if len(data) > 0:
            print(f"Sample Ep 3: {next((e for e in data if str(e.get('episode')) == '3'), 'Not Found')}")
    else:
        print("Key not found in cache.")
except Exception as e:
    print(f"DB Error: {e}")

print("\n--- KODI ERRORS ---")
# Check Kodi logs for errors during details lookup
try:
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "getepisodedetails" in line or "Error" in line or "WARNING" in line:
                if "metadata.anime.otaku.python" in line or "VideoInfoScanner" in line:
                    print(line.strip())
except Exception as e:
    print(f"Log Error: {e}")
