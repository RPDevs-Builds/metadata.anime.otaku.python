import re
import urllib.request
import urllib.parse
import json
import xbmcgui
import xbmcplugin
from .utils import logger

def parse_nfo_and_search(handle, nfo_text):
    if isinstance(nfo_text, bytes):
        nfo_text = nfo_text.decode('utf-8', 'replace')
        
    anilist_id = None
    mal_id = None
    
    # Try finding explicit IDs or URLs
    mal_match = re.search(r'myanimelist\.net/anime/(\d+)', nfo_text, re.I) or re.search(r'<uniqueid type="mal_id".*>(\d+)</uniqueid>', nfo_text, re.I)
    anilist_match = re.search(r'anilist\.co/anime/(\d+)', nfo_text, re.I) or re.search(r'<uniqueid type="anilist_id".*>(\d+)</uniqueid>', nfo_text, re.I)
    
    if anilist_match:
        anilist_id = anilist_match.group(1)
    elif mal_match:
        mal_id = mal_match.group(1)
        # Use our local mapping DB to get Anilist ID
        from .db_connector import get_mapping
        mapping = get_mapping(mal_id, 'mal_id')
        if mapping:
            anilist_id = mapping.get('anilist_id')
            
    if anilist_id:
        logger(f"NFO Parser found AniList ID: {anilist_id}")
        query = '''
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            idMal
            title { romaji english }
            seasonYear
          }
        }
        '''
        try:
            req = urllib.request.Request(
                'https://graphql.anilist.co',
                data=json.dumps({'query': query, 'variables': {'id': int(anilist_id)}}).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                anime = data.get('data', {}).get('Media')
                
                if anime:
                    title_eng = anime['title'].get('english') or anime['title'].get('romaji')
                    year = anime.get('seasonYear', '')
                    mal_id = anime.get('idMal', mal_id or '')
                    
                    liz = xbmcgui.ListItem(f"{title_eng} ({year})", offscreen=True)
                    url_qs = urllib.parse.urlencode({'mal_id': mal_id, 'tvdb_id': '', 'title_eng': title_eng})
                    ep_guide_url = f"plugin://metadata.anime.otaku.python/?action=getepisodelist&url={urllib.parse.quote(url_qs)}"
                    
                    liz.setProperty('episodeguide', ep_guide_url)
                    details_url = f"?action=getdetails&url={urllib.parse.quote(url_qs)}"
                    
                    xbmcplugin.addDirectoryItem(handle=handle, url=details_url, listitem=liz, isFolder=True)
                    xbmcplugin.endOfDirectory(handle, succeeded=True)
                    return
        except Exception as e:
            logger(f"NFO AniList fetch failed: {e}", level="ERROR")
            
    # Fallback if no NFO matched
    logger("NFO Parser found no valid anime IDs, falling back...", level="WARNING")
    xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
