import urllib.request
import json
from ..utils import logger

def get_mappings(mal_id):
    url = f'https://api.ani.zip/mappings?mal_id={mal_id}'
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger(f"AniZip Error: {e}", level="ERROR")
    return None
