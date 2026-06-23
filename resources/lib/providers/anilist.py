# -*- coding: utf-8 -*-
import requests
from ..utils import logger

def search_anime(query):
    """Searches AniList GraphQL API and returns a list of dictionaries with ID and Title."""
    logger(f"AniList API Search Triggered: {query}")
    url = 'https://graphql.anilist.co'
    
    graphql_query = '''
    query ($search: String) {
      Page(page: 1, perPage: 10) {
        media(search: $search, type: ANIME) {
          id
          title {
            romaji
            english
          }
        }
      }
    }
    '''
    
    variables = {'search': query}
    
    try:
        response = requests.post(url, json={'query': graphql_query, 'variables': variables}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for media in data.get('data', {}).get('Page', {}).get('media', []):
            # Prefer English title, fallback to Romaji
            title = media.get('title', {}).get('english') or media.get('title', {}).get('romaji')
            results.append({
                'id': media['id'],
                'title': title
            })
            
        return results
        
    except Exception as e:
        logger(f"AniList API failed: {e}", level="ERROR")
        return []
