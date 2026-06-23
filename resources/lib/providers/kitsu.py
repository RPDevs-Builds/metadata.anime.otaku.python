import urllib.request
import json
from ..utils import logger

def get_episodes(kitsu_id):
    if not kitsu_id:
        return []
        
    url = f'https://kitsu.io/api/edge/anime/{kitsu_id}/episodes'
    try:
        req = urllib.request.Request(
            f"{url}?page[limit]=20",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('data', [])
    except Exception as e:
        logger(f"Kitsu Error: {e}", level="ERROR")
    return []
