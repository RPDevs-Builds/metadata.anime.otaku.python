# -*- coding: utf-8 -*-
import sys
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import get_mapping
from .providers import anilist, tvdb
from .metadata_engine import fetch_all_metadata, get_cached_episode
from .database_sync import init_db
from .utils import logger

# Initialize local SQLite cache schema
init_db()

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
    elif action == 'getartwork':
        anime_id = params.get('id', [''])[0]
        get_artwork(handle, anime_id)

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
                'tvdb_season': mapping.get('thetvdb_season', ''),
                'title_eng': anime.get('title', '')
            }
            
            # Clean out any empty/null values and encode
            url_params = {k: v for k, v in url_params.items() if v}
            encoded_url = urllib.parse.urlencode(url_params)
            
            # Prefer the official MAL title if available
            display_title = mapping.get('mal_title', anime.get('title', 'Unknown'))
            liz = xbmcgui.ListItem(display_title, offscreen=True)
            
            xbmcplugin.addDirectoryItem(handle=handle, url=encoded_url, listitem=liz, isFolder=True)
            
    xbmcplugin.endOfDirectory(handle)

def get_series_details(handle, url):
    ids = dict(urllib.parse.parse_qsl(url))
    
    tvdb_id = ids.get('tvdb_id')
    anilist_id = ids.get('anilist_id')
    imdb_id = ids.get('imdb_id')
    
    tvdb_data = tvdb.get_series_details_api(tvdb_id) if tvdb_id else {}
    anilist_data = anilist.get_anime_details(anilist_id) if anilist_id else {}
    
    title = (anilist_data.get('title', {}).get('romaji') or 
             anilist_data.get('title', {}).get('english') or 
             'Unknown Anime')
             
    liz = xbmcgui.ListItem(title, offscreen=True)
    
    unique_ids = {}
    if tvdb_id: unique_ids['tvdb'] = str(tvdb_id)
    if imdb_id: unique_ids['imdb'] = str(imdb_id)
    if ids.get('tmdb_id'): unique_ids['tmdb'] = str(ids.get('tmdb_id'))
    if anilist_id: unique_ids['anilist'] = str(anilist_id)
    if ids.get('mal_id'): unique_ids['mal_id'] = str(ids.get('mal_id'))
    
    # Backward compatibility metadata
    info_dict = {
        'title': title,
        'tvshowtitle': title,
        'plot': anilist_data.get('description', ''),
        'genre': anilist_data.get('genres', []),
        'studio': anilist_data.get('studio', ''),
        'status': tvdb_data.get('status', 'Continuing'),
        'premiered': anilist_data.get('premiered', ''),
        'mediatype': 'tvshow',
        'episodeguide': urllib.parse.quote(url)
    }
    
    year = anilist_data.get('year')
    if year:
        info_dict['year'] = int(year)
        
    liz.setInfo('video', info_dict)
    
    # Artwork mapping
    poster = anilist_data.get('poster')
    banner = anilist_data.get('banner')
    
    art_dict = {}
    if poster:
        art_dict['poster'] = poster
        liz.addAvailableArtwork(poster, 'poster')
    if banner:
        art_dict['banner'] = banner
        art_dict['fanart'] = banner
        liz.addAvailableArtwork(banner, 'banner')
        liz.addAvailableArtwork(banner, 'fanart')
    if art_dict:
        liz.setArt(art_dict)
        
    # Modern InfoTagVideo mapping (Kodi 20+)
    try:
        vtag = liz.getVideoInfoTag()
        vtag.setTitle(title)
        vtag.setTvShowTitle(title)
        vtag.setPlot(anilist_data.get('description', ''))
        vtag.setGenres(anilist_data.get('genres', []))
        vtag.setStudios([anilist_data.get('studio', '')] if anilist_data.get('studio') else [])
        vtag.setTvShowStatus(tvdb_data.get('status', 'Continuing'))
        vtag.setMediaType('tvshow')
        if year:
            vtag.setYear(int(year))
        if anilist_data.get('premiered'):
            vtag.setPremiered(anilist_data.get('premiered'))
        vtag.setEpisodeGuide(urllib.parse.quote(url))
        vtag.setUniqueIDs(unique_ids, 'mal_id' if 'mal_id' in unique_ids else 'tvdb')
        
        if poster:
            vtag.addAvailableArtwork(poster, 'poster')
        if banner:
            vtag.addAvailableArtwork(banner, 'banner')
            vtag.addAvailableArtwork(banner, 'fanart')
    except Exception as e:
        logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
        
    liz.setUniqueIDs(unique_ids, 'mal_id' if 'mal_id' in unique_ids else 'tvdb')
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)

def get_episode_list(handle, url):
    ids = dict(urllib.parse.parse_qsl(urllib.parse.unquote(url)))
    mal_id = ids.get('mal_id')
    tvdb_id = ids.get('tvdb_id')
    title_eng = ids.get('title_eng')
    
    if not mal_id and not tvdb_id:
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return
        
    episodes = fetch_all_metadata(mal_id, tvdb_id, title_eng)
    if not episodes:
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return
        
    last_liz = None
    for ep in episodes:
        title = ep.get('title', 'Episode')
        liz = xbmcgui.ListItem(title, offscreen=True)
        
        # Backward compatibility details
        details = {
            'title': title,
            'plot': ep.get('plot', ''),
            'aired': ep.get('aired', ''),
            'premiered': ep.get('aired', ''),
            'season': ep.get('season', 1),
            'episode': ep.get('episode', 1),
            'mediatype': 'episode'
        }
        liz.setInfo('video', details)
        
        image = ep.get('image', '')
        if image:
            liz.addAvailableArtwork(image, 'thumb')
            liz.setArt({'thumb': image})
            
        # Modern InfoTagVideo mapping (Kodi 20+)
        try:
            vtag = liz.getVideoInfoTag()
            vtag.setTitle(title)
            vtag.setSeason(int(ep.get('season', 1)))
            vtag.setEpisode(int(ep.get('episode', 1)))
            vtag.setMediaType('episode')
            if ep.get('plot'):
                vtag.setPlot(ep.get('plot'))
            if ep.get('aired'):
                vtag.setFirstAired(ep.get('aired'))
                vtag.setPremiered(ep.get('aired'))
            if image:
                vtag.addAvailableArtwork(image, 'thumb')
        except Exception as e:
            logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
            
        # Build episode url to pass required identifiers for details phase
        ep_url = urllib.parse.urlencode({
            'mal_id': mal_id,
            'season': ep.get('season', 1),
            'episode': ep.get('episode', 1),
            'tvdb_id': ep.get('tvdb_id', '')
        })
        xbmcplugin.addDirectoryItem(handle=handle, url=ep_url, listitem=liz, isFolder=True)
        last_liz = liz
        
    if last_liz:
        try:
            xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=last_liz)
        except Exception:
            pass
            
    xbmcplugin.endOfDirectory(handle)

def get_episode_details(handle, url):
    params = dict(urllib.parse.parse_qsl(url))
    mal_id = params.get('mal_id')
    season = params.get('season')
    episode = params.get('episode')
    
    if not mal_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    # Read from local SQLite cache instead of fetching again!
    ep = get_cached_episode(mal_id, season, episode)
    
    if not ep:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    title = ep.get('title', 'Episode')
    liz = xbmcgui.ListItem(title, offscreen=True)
    
    details = {
        'title': title,
        'plot': ep.get('plot', ''),
        'aired': ep.get('aired', ''),
        'premiered': ep.get('aired', ''),
        'season': ep.get('season', 1),
        'episode': ep.get('episode', 1),
        'mediatype': 'episode'
    }
    
    liz.setInfo('video', details)
    
    image = ep.get('image', '')
    if image:
        liz.addAvailableArtwork(image, 'thumb')
        liz.setArt({'thumb': image})
        
    unique_ids = {}
    if params.get('tvdb_id'): unique_ids['tvdb'] = str(params.get('tvdb_id'))
    unique_ids['mal_id'] = str(mal_id)
    
    # Modern InfoTagVideo mapping (Kodi 20+)
    try:
        vtag = liz.getVideoInfoTag()
        vtag.setTitle(title)
        vtag.setSeason(int(ep.get('season', 1)))
        vtag.setEpisode(int(ep.get('episode', 1)))
        vtag.setMediaType('episode')
        if ep.get('plot'):
            vtag.setPlot(ep.get('plot'))
        if ep.get('aired'):
            vtag.setFirstAired(ep.get('aired'))
            vtag.setPremiered(ep.get('aired'))
        if image:
            vtag.addAvailableArtwork(image, 'thumb')
        vtag.setUniqueIDs(unique_ids, 'mal_id')
    except Exception as e:
        logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
        
    liz.setUniqueIDs(unique_ids, 'mal_id')
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)

def get_artwork(handle, anime_id):
    logger(f"Get Artwork request for ID: {anime_id}")
    if not anime_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    # Map MAL ID / default ID to AniList ID if needed
    mapping = get_mapping(anime_id, 'mal_id')
    anilist_id = mapping.get('anilist_id') if mapping else anime_id
    
    anilist_data = anilist.get_anime_details(anilist_id) if anilist_id else {}
    
    liz = xbmcgui.ListItem(str(anime_id), offscreen=True)
    
    poster = anilist_data.get('poster')
    banner = anilist_data.get('banner')
    
    art_dict = {}
    if poster:
        art_dict['poster'] = poster
        liz.addAvailableArtwork(poster, 'poster')
    if banner:
        art_dict['banner'] = banner
        art_dict['fanart'] = banner
        liz.addAvailableArtwork(banner, 'banner')
        liz.addAvailableArtwork(banner, 'fanart')
    if art_dict:
        liz.setArt(art_dict)
        
    try:
        vtag = liz.getVideoInfoTag()
        if poster:
            vtag.addAvailableArtwork(poster, 'poster')
        if banner:
            vtag.addAvailableArtwork(banner, 'banner')
            vtag.addAvailableArtwork(banner, 'fanart')
    except Exception as e:
        logger(f"Error setting VideoInfoTag artwork: {e}", level="WARNING")
        
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)
