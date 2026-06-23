# -*- coding: utf-8 -*-
import requests
from ..utils import logger

# Replace this with your actual TVDB v4 API Token
# Or switch to TMDB if you want a free, open alternative.
TVDB_TOKEN = "YOUR_TVDB_BEARER_TOKEN_HERE"
BASE_URL = "https://api4.thetvdb.com/v4"

def get_headers():
    return {
        "Authorization": f"Bearer {TVDB_TOKEN}",
        "Accept": "application/json"
    }

def get_series_data(tvdb_id):
    """Fetches high-level show data like the poster, plot, and genres."""
    logger(f"TVDB API: Fetching series {tvdb_id}")
    
    try:
        url = f"{BASE_URL}/series/{tvdb_id}/extended"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                'seriesName': data.get('name', 'Unknown'),
                'overview': data.get('overview', ''),
                'genre': [g.get('name') for g in data.get('genres', [])],
                'siteRating': data.get('score', 0.0),
                'poster': data.get('image', ''),
                'fanart': data.get('artworks', [{}])[0].get('image', '') if data.get('artworks') else ''
            }
    except Exception as e:
        logger(f"TVDB Series Data Failed: {e}", level="ERROR")
        
    # Fallback Stub
    return {
        'seriesName': f"Show {tvdb_id}",
        'overview': "Metadata could not be loaded from TVDB.",
    }

def get_all_episodes(tvdb_id):
    """Fetches a list of all S01E01 mapped episodes."""
    logger(f"TVDB API: Fetching episodes for series {tvdb_id}")
    
    try:
        url = f"{BASE_URL}/series/{tvdb_id}/episodes/default"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            episodes = response.json().get('data', {}).get('episodes', [])
            results = []
            for ep in episodes:
                results.append({
                    'id': ep.get('id'),
                    'title': ep.get('name', f"Episode {ep.get('number')}"),
                    'season': ep.get('seasonNumber', 1),
                    'episode': ep.get('number', 1)
                })
            return results
    except Exception as e:
        logger(f"TVDB Episode List Failed: {e}", level="ERROR")
        
    # Fallback Stub
    return [{'id': 1, 'title': 'Episode 1', 'season': 1, 'episode': 1}]

def get_episode_data(ep_id):
    """Fetches granular metadata (thumbnail, plot) for a specific episode."""
    logger(f"TVDB API: Fetching episode details for {ep_id}")
    
    try:
        url = f"{BASE_URL}/episodes/{ep_id}/extended"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                'title': data.get('name', ''),
                'overview': data.get('overview', ''),
                'firstAired': data.get('aired', ''),
                'image': data.get('image', '')
            }
    except Exception as e:
        logger(f"TVDB Episode Data Failed: {e}", level="ERROR")
        
    # Fallback Stub
    return {}
