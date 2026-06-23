# -*- coding: utf-8 -*-
import requests
from ..utils import logger

# Note: You need a valid TVDB v4 API Token
def get_series_details_api(tvdb_id):
    logger(f"TVDB Series Details Request for {tvdb_id}")
    if not tvdb_id:
        return {}
        
    return {
        'seriesName': f"Show {tvdb_id}",
        'overview': "Anime metadata provided via Otaku mappings.",
        'poster': '',
        'fanart': '',
        'status': 'Continuing',
        'firstAired': '2026-01-01'
    }

def get_series_episodes_api(tvdb_id):
    logger(f"TVDB Series Episodes Request for {tvdb_id}")
    if not tvdb_id:
        return []
        
    # Returns a list of dicts with expected keys
    return [
        {
            'id': 1001,
            'episodeName': 'Stub Episode 1',
            'firstAired': '2026-01-01',
            'airedSeason': 1,
            'airedEpisodeNumber': 1
        },
        {
            'id': 1002,
            'episodeName': 'Stub Episode 2',
            'firstAired': '2026-01-08',
            'airedSeason': 1,
            'airedEpisodeNumber': 2
        }
    ]

def get_episode_details_api(ep_id):
    logger(f"TVDB Episode Details Request for {ep_id}")
    if not ep_id:
        return {}
        
    return {
        'id': ep_id,
        'episodeName': f'Stub Episode {ep_id}',
        'overview': 'This is a stub episode plot from TVDB.',
        'firstAired': '2026-01-01',
        'airedSeason': 1,
        'airedEpisodeNumber': 1,
        'image': ''
    }

