# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
from ..utils import logger

try:
    import xbmcaddon
except ImportError:
    pass

BASE_URL = "https://webservice.fanart.tv/v3"

def get_art(tvdb_id=None, tmdb_id=None, mtype='tv'):
    """
    Fetch premium artwork from Fanart.tv.
    mtype should be 'tv' or 'movies'.
    For 'tv', tvdb_id is preferred but tmdb_id can work if API supports it.
    For 'movies', tmdb_id is required.
    """
    try:
        addon = xbmcaddon.Addon('metadata.anime.otaku.python')
        api_key = addon.getSetting('fanart_tv_api_key') or ''
        title_language_idx = addon.getSetting('indexer_title_language')
        language_pref = 'ja' if title_language_idx == 'Romaji' else 'en'
    except Exception:
        api_key = ''
        language_pref = 'en'
        
    if not api_key:
        return {}
        
    target_id = tmdb_id if mtype == 'movies' else (tvdb_id or tmdb_id)
    if not target_id:
        return {}
        
    url = f"{BASE_URL}/{mtype}/{target_id}"
    req = urllib.request.Request(url, headers={'Api-Key': api_key})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            logger(f"Fanart.tv HTTP Error {e.code}: {e.reason}", level="ERROR")
        return {}
    except Exception as e:
        logger(f"Fanart.tv connection error: {e}", level="ERROR")
        return {}
        
    art = {}
    lang_prefs = ['en', 'ja', '']
    
    def extract_items(data_key, limit=None):
        if data.get(data_key):
            items = [item.get('url') for item in data[data_key] if item.get('lang') in lang_prefs]
            return items[:limit] if limit else items
        return []

    if mtype == 'movies':
        fanart_items = extract_items('moviebackground')
        if fanart_items: art['fanart'] = fanart_items
        
        thumb_items = extract_items('moviethumb')
        if thumb_items: art['thumb'] = thumb_items
        
        clearart_items = extract_items('hdmovieclearart') or extract_items('clearart')
        if clearart_items: art['clearart'] = clearart_items
        
        logos = data.get('hdmovielogo') or data.get('clearlogo') or []
    else:
        fanart_items = extract_items('showbackground')
        if fanart_items: art['fanart'] = fanart_items
        
        thumb_items = extract_items('tvthumb')
        if thumb_items: art['thumb'] = thumb_items
        
        clearart_items = extract_items('hdclearart') or extract_items('clearart')
        if clearart_items: art['clearart'] = clearart_items
        
        logos = data.get('hdtvlogo') or data.get('clearlogo') or []
        
    # Extract Clearlogos prioritising preferred language
    if logos:
        # Sort by ID (newest first, assuming higher ID is newer)
        logos = sorted([item for item in logos if item.get('lang') in lang_prefs], key=lambda x: int(x.get('id', 0)), reverse=True)
        logo_urls = []
        # Try to find preferred language logo
        preferred_logo = next((x['url'] for x in logos if x['lang'] == language_pref), None)
        if preferred_logo:
            logo_urls.append(preferred_logo)
        if not logo_urls:
            # Fallback to any valid language
            any_logo = next((x['url'] for x in logos), None)
            if any_logo:
                logo_urls.append(any_logo)
                
        if logo_urls:
            art['clearlogo'] = logo_urls
            
    return art
