# -*- coding: utf-8 -*-
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import translate_anime_id
from .providers import anilist, tvdb
from .utils import logger

def router(action, args):
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

def find_show(handle, query):
    results = anilist.search_anime(query)
    for anime in results:
        # Query your local anime_mappings.db
        mapping = translate_anime_id(anime['id'], source_type='anilist_id')
        if mapping and mapping.get('thetvdb_id'):
            li = xbmcgui.ListItem(anime['title'])
            url = f"tvdb_id={mapping['thetvdb_id']}&anilist_id={anime['id']}"
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(handle)

def get_show_details(handle, url_params):
    params = dict(urllib.parse.parse_qsl(url_params))
    tvdb_id = params.get('tvdb_id')
    show_details = tvdb.get_series_data(tvdb_id)
    info = {
        'title': show_details.get('seriesName'),
        'plot': show_details.get('overview'),
        'episodeguide': url_params # Critical hand-off to step 3
    }
    li = xbmcgui.ListItem(info['title'])
    li.setInfo('video', info)
    li.setArt({'poster': show_details.get('poster')})
    xbmcplugin.setResolvedUrl(handle, True, li)

def get_episode_list(handle, url_params):
    params = dict(urllib.parse.parse_qsl(url_params))
    tvdb_id = params.get('tvdb_id')
    episodes = tvdb.get_all_episodes(tvdb_id)
    for ep in episodes:
        li = xbmcgui.ListItem(ep['title'])
        ep_url = f"tvdb_ep_id={ep['id']}&season={ep['season']}&episode={ep['episode']}"
        xbmcplugin.addDirectoryItem(handle=handle, url=ep_url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(handle)

def get_episode_details(handle, url_params):
    params = dict(urllib.parse.parse_qsl(url_params))
    ep_id = params.get('tvdb_ep_id')
    ep_data = tvdb.get_episode_data(ep_id)
    info = {
        'title': ep_data.get('title'),
        'plot': ep_data.get('overview'),
        'season': int(params.get('season', 0)),
        'episode': int(params.get('episode', 0))
    }
    li = xbmcgui.ListItem(info['title'])
    li.setInfo('video', info)
    xbmcplugin.setResolvedUrl(handle, True, li)
