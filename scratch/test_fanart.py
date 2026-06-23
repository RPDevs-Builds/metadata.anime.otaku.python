import os
import sys
from unittest.mock import MagicMock

# Mock Kodi modules to run standalone
sys.modules['xbmc'] = MagicMock()
sys.modules['xbmcplugin'] = MagicMock()
sys.modules['xbmcgui'] = MagicMock()

addon_mock = MagicMock()
addon_mock.getSetting.side_effect = lambda k: {
    'fanart_tv_api_key': '62fd37f8f94cb4c1f6de720a463ce8c9',
    'indexer_title_language': 'English'
}.get(k, '')
xbmcaddon_mock = MagicMock()
xbmcaddon_mock.Addon.return_value = addon_mock
sys.modules['xbmcaddon'] = xbmcaddon_mock

sys.modules['xbmcvfs'] = MagicMock()

# Add parent path to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resources.lib.providers.fanart import get_art

def main():
    print("Testing Fanart.tv integration...")
    
    # Attack on Titan TVDB: 267440, TMDb: 1429
    tv_art = get_art(tvdb_id='267440', tmdb_id='1429', mtype='tv')
    print("\n--- TV Show (Attack on Titan) ---")
    if tv_art.get('clearlogo'):
        print(f"Clearlogo: {tv_art['clearlogo'][0]}")
    if tv_art.get('clearart'):
        print(f"Clearart: {tv_art['clearart'][0]}")
    if tv_art.get('thumb'):
        print(f"Thumb count: {len(tv_art['thumb'])}")
        
    # Your Name. TMDb: 372058
    movie_art = get_art(tmdb_id='372058', mtype='movies')
    print("\n--- Movie (Your Name.) ---")
    if movie_art.get('clearlogo'):
        print(f"Clearlogo: {movie_art['clearlogo'][0]}")
    if movie_art.get('clearart'):
        print(f"Clearart: {movie_art['clearart'][0]}")
    if movie_art.get('fanart'):
        print(f"Background count: {len(movie_art['fanart'])}")

if __name__ == "__main__":
    main()
