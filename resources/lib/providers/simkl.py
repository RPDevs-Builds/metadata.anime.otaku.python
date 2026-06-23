import urllib.request
import json
import xbmcaddon
from ..utils import logger

ADDON = xbmcaddon.Addon()

def get_episodes(simkl_id):
    if not simkl_id:
        return []
        
    client_id = ADDON.getSetting('simkl_api_key')
    if not client_id:
        return []
        
    url = f'https://api.simkl.com/anime/episodes/{simkl_id}'
    try:
        req = urllib.request.Request(
            f"{url}?extended=full&client_id={client_id}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger(f"Simkl Error: {e}", level="ERROR")
    return []

def get_ratings(simkl_id):
    if not simkl_id:
        return {}
        
    client_id = ADDON.getSetting('simkl_api_key')
    if not client_id:
        return {}
        
    url = f'https://api.simkl.com/ratings?simkl={simkl_id}&client_id={client_id}'
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger(f"Simkl Ratings Error: {e}", level="ERROR")
    return {}
