import urllib.request
import json
from ..utils import logger

def get_episodes(mal_id):
    url = f'https://api.jikan.moe/v4/anime/{mal_id}/episodes'
    episodes = []
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            episodes.extend(res.get('data', []))
            return episodes
    except Exception as e:
        logger(f"Jikan Error: {e}", level="ERROR")
    return episodes
