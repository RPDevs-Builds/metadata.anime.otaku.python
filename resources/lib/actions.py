# -*- coding: utf-8 -*-
import sys
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import get_mapping
from .providers import anilist, tvdb
from .utils import logger

def router(query_string, args):
    handle = int(args[1])
    
    if query_string.startswith('?'):
        query_string = query_string[1:]
    
    params = urllib.parse.parse_qs(query_string)
    action = params.get('action', [''])[0]
    
    if action == 'find':
        title = params.get('title', [''])[0]
        find_show(handle, title)
    elif action == 'getdetails':
        url = params.get('url', [''])[0]
        get_series_details(handle, url)
    elif action == 'getepisodelist':
        url = params.get('url', [''])[0]
        get_episode_list(handle, url)
    elif action == 'getepisodedetails':
        url = params.get('url', [''])[0]
        get_episode_details(handle, url)

def find_show(handle, title):
    results = anilist.search_anime(title)
    
    for anime in results:
        mapping = get_mapping(anime['id'], 'anilist_id')
        
        if mapping:
            url_params = {
                'anilist_id': mapping.get('anilist_id', ''),
                'mal_id': mapping.get('mal_id', ''),
                'tvdb_id': mapping.get('thetvdb_id', ''),
                'tmdb_id': mapping.get('themoviedb_id', ''),
                'imdb_id': mapping.get('imdb_id', ''),
                'tvdb_season': mapping.get('thetvdb_season', '')
            }
            
            # Clean out any empty/null values and encode
            url_params = {k: v for k, v in url_params.items() if v}
            encoded_url = urllib.parse.urlencode(url_params)
            
            # Prefer the official MAL title if available
            display_title = mapping.get('mal_title', anime['title'])
            liz = xbmcgui.ListItem(display_title, offscreen=True)
            
            xbmcplugin.addDirectoryItem(handle=handle, url=encoded_url, listitem=liz, isFolder=True)
            
    xbmcplugin.endOfDirectory(handle)

def get_series_details(handle, url):
    ids = dict(urllib.parse.parse_qsl(url))
    
    tvdb_id = ids.get('tvdb_id')
    anilist_id = ids.get('anilist_id')
    imdb_id = ids.get('imdb_id')
    
    tvdb_data = tvdb.get_series_details_api(tvdb_id)
    anilist_data = anilist.get_anime_details(anilist_id)
    
    title = anilist_data.get('title', {}).get('romaji', 'Unknown Anime')
    liz = xbmcgui.ListItem(title, offscreen=True)
    
    liz.setInfo('video', {
        'plot': anilist_data.get('description', ''),
        'genre': anilist_data.get('genres', []),
        'studio': anilist_data.get('studio', ''),
        'status': tvdb_data.get('status', ''),
        'premiered': tvdb_data.get('firstAired', ''),
        'mediatype': 'tvshow'
    })
    
    unique_ids = {}
    if tvdb_id: unique_ids['tvdb'] = str(tvdb_id)
    if imdb_id: unique_ids['imdb'] = str(imdb_id)
    if ids.get('tmdb_id'): unique_ids['tmdb'] = str(ids.get('tmdb_id'))
    if anilist_id: unique_ids['anilist'] = str(anilist_id)
        
    liz.setUniqueIDs(unique_ids, 'tvdb')
    liz.setProperty('episodeguide', urllib.parse.quote(url))
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)

def get_episode_list(handle, url):
    ids = dict(urllib.parse.parse_qsl(urllib.parse.unquote(url)))
    tvdb_id = ids.get('tvdb_id')
    tvdb_season = ids.get('tvdb_season', '')
    
    if not tvdb_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    episodes = tvdb.get_series_episodes_api(tvdb_id)
    if not episodes:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    for ep in episodes:
        # If mapping strictly requires a season, we might filter here
        # But for now, just output all episodes to let Kodi handle it.
        liz = xbmcgui.ListItem(ep.get('episodeName', 'Episode'), offscreen=True)
        details = {
            'title': ep.get('episodeName', 'Episode'),
            'aired': ep.get('firstAired', ''),
            'season': ep.get('airedSeason', 1),
            'episode': ep.get('airedEpisodeNumber', 1)
        }
        
        liz.setInfo('video', details)
        
        # Build episode url
        ep_url = urllib.parse.urlencode({'tvdb_id': tvdb_id, 'ep_id': ep.get('id')})
        xbmcplugin.addDirectoryItem(handle=handle, url=ep_url, listitem=liz, isFolder=True)
        
    xbmcplugin.endOfDirectory(handle)

def get_episode_details(handle, url):
    params = dict(urllib.parse.parse_qsl(url))
    ep_id = params.get('ep_id')
    
    if not ep_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    ep = tvdb.get_episode_details_api(ep_id)
    if not ep:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    liz = xbmcgui.ListItem(ep.get('episodeName', 'Episode'), offscreen=True)
    details = {
        'title': ep.get('episodeName', 'Episode'),
        'plot': ep.get('overview', ''),
        'premiered': ep.get('firstAired', ''),
        'aired': ep.get('firstAired', ''),
        'season': ep.get('airedSeason', 1),
        'episode': ep.get('airedEpisodeNumber', 1),
        'mediatype': 'episode'
    }
    
    liz.setInfo('video', details)
    liz.setUniqueIDs({'tvdb': str(ep.get('id', ep_id))}, 'tvdb')
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)
