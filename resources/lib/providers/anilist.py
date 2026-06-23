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
