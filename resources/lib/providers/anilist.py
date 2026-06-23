# -*- coding: utf-8 -*-
import requests
from ..utils import logger

def search_anime(query):
    url = 'https://graphql.anilist.co'
    query_str = '''
    query ($search: String) {
      Page(page: 1, perPage: 10) {
        media(search: $search, type: ANIME) {
          id
          title { romaji }
        }
      }
    }
    '''
    variables = {'search': query}
    try:
        response = requests.post(url, json={'query': query_str, 'variables': variables}, timeout=10)
        data = response.json()
        return [{'id': m['id'], 'title': m['title']['romaji']} 
                for m in data.get('data', {}).get('Page', {}).get('media', [])]
    except Exception as e:
        logger(f"AniList Search Error: {e}", level="ERROR")
        return []

def get_anime_details(anilist_id):
    if not anilist_id:
        return {}
        
    url = 'https://graphql.anilist.co'
    query_str = '''
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        id
        title { romaji english native }
        description
        genres
        studios(isMain: true) {
          nodes { name }
        }
      }
    }
    '''
    variables = {'id': int(anilist_id)}
    try:
        response = requests.post(url, json={'query': query_str, 'variables': variables}, timeout=10)
        data = response.json()
        media = data.get('data', {}).get('Media', {})
        
        # Format studios correctly
        studios = media.get('studios', {}).get('nodes', [])
        studio_name = studios[0]['name'] if studios else ''
        
        return {
            'title': media.get('title', {}),
            'description': media.get('description', ''),
            'genres': media.get('genres', []),
            'studio': studio_name
        }
    except Exception as e:
        logger(f"AniList Details Error: {e}", level="ERROR")
        return {}

