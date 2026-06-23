# -*- coding: utf-8 -*-
import requests
from ..utils import logger

# Note: You need a valid TVDB v4 API Token
def get_series_data(tvdb_id):
    logger(f"TVDB Request for {tvdb_id}")
    # You would implement your requests.get() here using your TVDB API key
    # returning a dict with keys: 'seriesName', 'overview', 'poster', 'fanart'
    return {
        'seriesName': f"Show {tvdb_id}",
        'overview': "Anime metadata provided via Otaku mappings.",
        'poster': '',
        'fanart': ''
    }

def get_all_episodes(tvdb_id):
    # Returns a list of dicts: {'id', 'title', 'season', 'episode'}
    return [{'id': 1, 'title': 'Episode 1', 'season': 1, 'episode': 1}]

def get_episode_data(ep_id):
    # Returns episode metadata
    return {'title': 'Episode 1', 'overview': 'Plot', 'firstAired': '2026-01-01', 'image': ''}
