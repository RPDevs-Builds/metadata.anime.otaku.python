# -*- coding: utf-8 -*-
import urllib.request
import json
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
    api_key = get_api_key()
    try:
        url = f"{BASE_URL}/tv/{tmdb_id}?api_key={api_key}&language=en-US"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            genres = [g.get('name') for g in data.get('genres', [])]
            poster_path = data.get('poster_path', '')
            backdrop_path = data.get('backdrop_path', '')
            
            return {
                'seriesName': data.get('name', 'Unknown Title'),
                'overview': data.get('overview', ''),
                'genre': genres,
                'siteRating': data.get('vote_average', 0.0),
                'votes': data.get('vote_count', 0),
                'first_air_date': data.get('first_air_date', ''),
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
                'fanart': f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else ''
            }
    except Exception as e:
        logger(f"TMDb Series parsing fault: {e}", level="ERROR")
        
    return {'seriesName': f"TMDb Show {tmdb_id}", 'overview': "Metadata extraction bypassed."}

def get_all_episodes(tmdb_id):
    """Iterates over available structural seasons to compile a master episode manifest."""
    logger(f"TMDb API: Fetching full season layout for ID {tmdb_id}")
    api_key = get_api_key()
    results = []
    try:
        url = f"{BASE_URL}/tv/{tmdb_id}?api_key={api_key}&language=en-US"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            seasons = json.loads(response.read().decode('utf-8')).get('seasons', [])
            
        for season in seasons:
            season_num = season.get('season_number', 0)
            
            season_url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_num}?api_key={api_key}&language=en-US"
            s_req = urllib.request.Request(season_url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(s_req, timeout=10) as s_response:
                    episodes = json.loads(s_response.read().decode('utf-8')).get('episodes', [])
                    for ep in episodes:
                        results.append({
                            'id': ep.get('id'),
                            'title': ep.get('name', f"Episode {ep.get('episode_number')}"),
                            'season': season_num,
                            'episode': ep.get('episode_number', 1)
                        })
            except Exception as e:
                logger(f"TMDb index season {season_num} failure: {e}", level="ERROR")
        return results
    except Exception as e:
        logger(f"TMDb indexing loop failure: {e}", level="ERROR")
        
    return [{'id': 1, 'title': 'Episode 1 (Fallback)', 'season': 1, 'episode': 1}]

def get_episode_data(tmdb_id, season_num, episode_num):
    """Resolves granular contextual nodes for individual episodes."""
    api_key = get_api_key()
    try:
        url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_num}/episode/{episode_num}?api_key={api_key}&language=en-US"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
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

def get_movie_data(tmdb_id):
    """Fetches movie-specific metadata from TMDb."""
    logger(f"TMDb API: Fetching Movie details for ID {tmdb_id}")
    api_key = get_api_key()
    try:
        url = f"{BASE_URL}/movie/{tmdb_id}?api_key={api_key}&language=en-US"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            genres = [g.get('name') for g in data.get('genres', [])]
            poster_path = data.get('poster_path', '')
            backdrop_path = data.get('backdrop_path', '')
            
            return {
                'title': data.get('title', 'Unknown Title'),
                'overview': data.get('overview', ''),
                'genre': genres,
                'siteRating': data.get('vote_average', 0.0),
                'votes': data.get('vote_count', 0),
                'first_air_date': data.get('release_date', ''),
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '',
                'fanart': f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else ''
            }
    except Exception as e:
        logger(f"TMDb Movie parsing fault: {e}", level="ERROR")
        
    return {'title': f"TMDb Movie {tmdb_id}", 'overview': "Metadata extraction bypassed."}
