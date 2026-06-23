# -*- coding: utf-8 -*-
import requests
from ..utils import logger

DEFAULT_KEY = "af3a53eb387d57fc935e9128468b1899"
BASE_URL = "https://api.themoviedb.org/3"

def get_api_key():
    """Retrieves the api key from settings, falling back to default."""
    try:
        import xbmcaddon
        addon = xbmcaddon.Addon('metadata.anime.otaku.python')
        custom_key = addon.getSettingString('tmdb_api_key')
        if custom_key:
            return custom_key
    except Exception:
        pass
    return DEFAULT_KEY

def get_series_data(tmdb_id):
    """Fetches high-level series metrics including banners, plots, and rating scores."""
    logger(f"TMDb API: Fetching TV show details for ID {tmdb_id}")
    params = {
        "api_key": get_api_key(),
        "language": "en-US"
    }
    try:
        url = f"{BASE_URL}/tv/{tmdb_id}"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            genres = [g.get('name') for g in data.get('genres', [])]
            poster_path = data.get('poster_path', '')
            backdrop_path = data.get('backdrop_path', '')
            
            return {
                'seriesName': data.get('name', 'Unknown Title'),
                'overview': data.get('overview', ''),
                'genre': genres,
                'siteRating': data.get('vote_average', 0.0),
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
                'fanart': f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else ''
            }
    except Exception as e:
        logger(f"TMDb Series parsing fault: {e}", level="ERROR")
        
    return {'seriesName': f"TMDb Show {tmdb_id}", 'overview': "Metadata extraction bypassed."}

def get_all_episodes(tmdb_id):
    """Iterates over available structural seasons to compile a master episode manifest."""
    logger(f"TMDb API: Fetching full season layout for ID {tmdb_id}")
    params = {"api_key": get_api_key(), "language": "en-US"}
    results = []
    try:
        # First query the main show endpoint to learn how many seasons it actually has
        url = f"{BASE_URL}/tv/{tmdb_id}"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return results
            
        seasons = response.json().get('seasons', [])
        for season in seasons:
            season_num = season.get('season_number', 0)
            # Skip specials (Season 0) if you want a clean progression, or keep them
            
            season_url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_num}"
            s_response = requests.get(season_url, params=params, timeout=10)
            if s_response.status_code == 200:
                episodes = s_response.json().get('episodes', [])
                for ep in episodes:
                    results.append({
                        'id': ep.get('id'),
                        'title': ep.get('name', f"Episode {ep.get('episode_number')}"),
                        'season': season_num,
                        'episode': ep.get('episode_number', 1)
                    })
        return results
    except Exception as e:
        logger(f"TMDb indexing loop failure: {e}", level="ERROR")
        
    return [{'id': 1, 'title': 'Episode 1 (Fallback)', 'season': 1, 'episode': 1}]

def get_episode_data(tmdb_id, season_num, episode_num):
    """Resolves granular contextual nodes for individual episodes."""
    params = {"api_key": get_api_key(), "language": "en-US"}
    try:
        url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_num}/episode/{episode_num}"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            still_path = data.get('still_path', '')
            return {
                'title': data.get('name', ''),
                'overview': data.get('overview', ''),
                'firstAired': data.get('air_date', ''),
                'image': f"https://image.tmdb.org/t/p/w500{still_path}" if still_path else ''
            }
    except Exception as e:
        logger(f"TMDb episode node lookup failure: {e}", level="ERROR")
    return {}
