# -*- coding: utf-8 -*-
import os
import sqlite3
import xbmcaddon
import xbmcvfs
from .utils import logger

def get_db_path():
    addon = xbmcaddon.Addon('metadata.anime.otaku.python')
    addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
    return os.path.join(addon_path, 'resources', 'lib', 'anime_mappings.db')

def get_mapping(source_id, source_type='anilist_id'):
    """
    Queries anime_mappings.db and returns a dictionary of all cross-platform IDs.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        logger(f"Database missing at: {db_path}", level="ERROR")
        return None
        
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row  # Allows us to access columns by name like a dict
        cursor = conn.cursor()
        
        query = f"SELECT * FROM anime WHERE {source_type} = ?"
        cursor.execute(query, (str(source_id),))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger(f"Database Error: {e}", level="ERROR")
        return None
    finally:
        if 'conn' in locals():
            conn.close()
