# -*- coding: utf-8 -*-
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import translate_anime_id
from .providers import anilist, tvdb
from .utils import logger

def router(action, args):
    """Routes the Kodi scraper action to the correct function."""
    handle = int(args[1])
    
    if action == 'find':
        query = urllib.parse.unquote_plus(args[3])
        find_show(handle, query)
        
    elif action == 'getdetails':
        url = urllib.parse.unquote_plus(args[3])
        get_show_details(handle, url)
        
    elif action == 'getepisodelist':
        url = urllib.parse.unquote_plus(args[3])
        get_episode_list(handle, url)
        
    elif action == 'getepisodedetails':
        url = urllib.parse.unquote_plus(args[3])
        get_episode_details(handle, url)
        
    elif action == 'NfoUrl':
        # Used if user has local NFO files. Skip for now to force API scraping.
        pass 
    else:
        logger(f"Unhandled action received: {action}", level="WARNING")

def find_show(handle, query):
    """STEP 1: Search for the Anime using AniList."""
    results = anilist.search_anime(query)
    
    for anime in results:
        # Map AniList ID to TVDB ID locally
        mapping = translate_anime_id(anime['id'], source_type='anilist_id')
        
        if mapping and mapping.get('thetvdb_id'):
            li = xbmcgui.ListItem(anime['title'])
            
            # Pass the mapped IDs forward
            url = f"tvdb_id={mapping['thetvdb_id']}&anilist_id={anime['id']}"
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
            
    xbmcplugin.endOfDirectory(handle)

def get_show_details(handle, url_params):
    """STEP 2: Provide Kodi with the standard Western formatted TVDB details."""
    params = dict(urllib.parse.parse_qsl(url_params))
    tvdb_id = params.get('tvdb_id')
    
    show_details = tvdb.get_series_data(tvdb_id)
    
    info = {
        'title': show_details.get('seriesName', 'Unknown Title'),
        'plot': show_details.get('overview', ''),
        'genre': show_details.get('genre', []),
        'rating': show_details.get('siteRating', 0.0),
        'episodeguide': url_params # Triggers Step 3
    }
    
    li = xbmcgui.ListItem(info['title'])
    li.setInfo('video', info)
    li.setArt({'poster': show_details.get('poster', ''), 'fanart': show_details.get('fanart', '')})
    
    xbmcplugin.setResolvedUrl(handle, True, li)

def get_episode_list(handle, url_params):
    """STEP 3: Return a directory of all available episodes to Kodi."""
    params = dict(urllib.parse.parse_qsl(url_params))
    tvdb_id = params.get('tvdb_id')
    
    episodes = tvdb.get_all_episodes(tvdb_id)
    
    for ep in episodes:
        li = xbmcgui.ListItem(ep['title'])
        ep_url = f"tvdb_ep_id={ep['id']}&season={ep['season']}&episode={ep['episode']}"
        # isFolder MUST be False for episodes
        xbmcplugin.addDirectoryItem(handle=handle, url=ep_url, listitem=li, isFolder=False)
        
    xbmcplugin.endOfDirectory(handle)

def get_episode_details(handle, url_params):
    """STEP 4: Resolve the final metadata for a single episode."""
    params = dict(urllib.parse.parse_qsl(url_params))
    ep_id = params.get('tvdb_ep_id')
    
    ep_data = tvdb.get_episode_data(ep_id)
    
    info = {
        'title': ep_data.get('title', f"Episode {params.get('episode')}"),
        'plot': ep_data.get('overview', ''),
        'season': int(params.get('season', 0)),
        'episode': int(params.get('episode', 0)),
        'aired': ep_data.get('firstAired', '')
    }
    
    li = xbmcgui.ListItem(info['title'])
    li.setInfo('video', info)
    
    if ep_data.get('image'):
        li.setArt({'thumb': ep_data['image']})
        
    xbmcplugin.setResolvedUrl(handle, True, li)
