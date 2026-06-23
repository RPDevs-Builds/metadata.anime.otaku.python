# -*- coding: utf-8 -*-
import os
import sqlite3
import xbmcaddon
import xbmcvfs
from .utils import logger

def get_db_path():
    """
    Dynamically resolves the path to anime_mappings.db within Kodi.
    Follows path management conventions modeled after https://github.com/xbmc/metadata.tvdb.com_6.python.
    """
    addon = xbmcaddon.Addon('metadata.anime.otaku.python')
    
    # Check if an updated database exists in the user profile directory first
    profile_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    updated_db_path = os.path.join(profile_path, 'anime_mappings.db')
    if os.path.exists(updated_db_path):
        return updated_db_path
        
    # Fall back to the bundled database package within the addon directory
    addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
    return os.path.join(addon_path, 'resources', 'lib', 'anime_mappings.db')

def dict_factory(cursor, row):
    """
    Converts standard SQL tuple outputs into accessible Python dictionaries.
    Mapped mapping fields: anilist_id, mal_id, thetvdb_id, kitsu_id, tmdb_id.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def translate_anime_id(anime_id, source_type='anilist_id'):
    """
    Queries mapping tables built from data matching https://github_6.com/Goldenfreddy0703/Otaku
    to return cross-platform structural identity IDs.
    
    :param anime_id: int/str - The unique lookup identification key
    :param source_type: str - Column context to query (e.g., 'anilist_id', 'mal_id')
    :return: dict or None - Matched platform fields or fallback None
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        logger(f"Database schema array missing at target location: {db_path}", level="ERROR")
        return None

    conn = None
    try:
        # Open SQLite connection in read-only mode to safeguard multi-threaded library calls
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Parameterized dynamic query prevents column parsing extraction faults
        query = f"SELECT * FROM mappings WHERE {source_type} = ?"
        cursor.execute(query, (anime_id,))
        result = cursor.fetchone()
        
        return result

    except sqlite3.Error as e:
        logger(f"Database retrieval layer isolation fault: {e}", level="ERROR")
        return None
        
    finally:
        if conn:
            conn.close()
