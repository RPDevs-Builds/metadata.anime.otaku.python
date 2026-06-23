# -*- coding: utf-8 -*-
import urllib.request
import json
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
        req_data = json.dumps({'query': query_str, 'variables': variables}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
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
        coverImage {
          extraLarge
          large
          medium
        }
        bannerImage
        startDate {
          year
          month
          day
        }
      }
    }
    '''
    variables = {'id': int(anilist_id)}
    try:
        req_data = json.dumps({'query': query_str, 'variables': variables}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            media = data.get('data', {}).get('Media', {})
            
            # Format studios correctly
            studios = media.get('studios', {}).get('nodes', [])
            studio_name = studios[0]['name'] if studios else ''
            
            # Format startDate to premiered date
            start_date = media.get('startDate', {})
            year = start_date.get('year', '')
            month = start_date.get('month', '')
            day = start_date.get('day', '')
            premiered = ''
            if year and month and day:
                premiered = f"{year:04d}-{month:02d}-{day:02d}"
            elif year:
                premiered = f"{year:04d}-01-01"
                
            cover_image = media.get('coverImage', {})
            poster = cover_image.get('extraLarge') or cover_image.get('large') or cover_image.get('medium') or ''
            
            return {
                'title': media.get('title', {}),
                'description': media.get('description', ''),
                'genres': media.get('genres', []),
                'studio': studio_name,
                'poster': poster,
                'banner': media.get('bannerImage') or '',
                'year': year,
                'premiered': premiered
            }
    except Exception as e:
        logger(f"AniList Details Error: {e}", level="ERROR")
        return {}

