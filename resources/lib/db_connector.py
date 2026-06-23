# -*- coding: utf-8 -*-
import os
import sqlite3
import xbmcaddon
import xbmcvfs
from .utils import logger

def get_db_path():
    addon = xbmcaddon.Addon('metadata.anime.otaku.python')
    addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
    # Points to your anime_mappings.db in the lib folder
    return os.path.join(addon_path, 'resources', 'lib', 'anime_mappings.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def translate_anime_id(anime_id, source_type='anilist_id'):
    db_path = get_db_path()
    if not os.path.exists(db_path):
        logger(f"Database missing at: {db_path}", level="ERROR")
        return None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        query = f"SELECT * FROM anime WHERE {source_type} = ?"
        cursor.execute(query, (anime_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    except sqlite3.Error as e:
        logger(f"DB Error: {e}", level="ERROR")
        return None
