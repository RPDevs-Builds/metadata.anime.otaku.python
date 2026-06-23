# -*- coding: utf-8 -*-
import sys
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import translate_anime_id
from .providers import anilist, tvdb
from .utils import logger

def router(query_string, args):
    handle = int(args[1])
    
    # Remove the leading '?' and parse the query string into a dictionary
    if query_string.startswith('?'):
        query_string = query_string[1:]
    
    params = urllib.parse.parse_qs(query_string)
    
    # Extract the 'action' parameter safely
    action = params.get('action', [''])[0]
    
    if action == 'find':
        # Extract the title from the parameters instead of args[3]
        title = params.get('title', [''])[0]
        find_show(handle, title)
    # ... (Add remaining action calls here)

def find_show(handle, query):
    results = anilist.search_anime(query)
    for anime in results:
        mapping = translate_anime_id(anime['id'], source_type='anilist_id')
        if mapping and mapping.get('thetvdb_id'):
            li = xbmcgui.ListItem(anime['title'])
            url = f"tvdb_id={mapping['thetvdb_id']}&anilist_id={anime['id']}"
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
            
    # endOfDirectory must be called to tell Kodi we are done building the list
    xbmcplugin.endOfDirectory(handle)
