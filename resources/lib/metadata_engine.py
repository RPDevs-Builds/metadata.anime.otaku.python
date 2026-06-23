import concurrent.futures
import xbmcaddon
from .providers import anizip, jikan, kitsu, simkl, tvdb, anime_filler
from .database import get_cache, set_cache
from .utils import logger

ADDON = xbmcaddon.Addon()

def fetch_all_metadata(mal_id, tvdb_id, title_eng=None):
    cache_key = f"episode_meta_{mal_id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    meta_cache = {}

    def is_enabled(setting_key):
        val = str(ADDON.getSetting(setting_key)).lower()
        # Default to true if empty or explicitly true
        return val in ['true', '1', '']

    def fetch_anizip():
        if is_enabled('provider_anizip'):
            return ('anizip', anizip.get_mappings(mal_id))
        return ('anizip', None)

    def fetch_jikan():
        if is_enabled('provider_jikan'):
            return ('jikan', jikan.get_episodes(mal_id))
        return ('jikan', [])

    def fetch_kitsu():
        if is_enabled('provider_kitsu'):
            # we don't strictly have kitsu_id here yet, assume mapping logic handles it
            return ('kitsu', [])
        return ('kitsu', [])

    def fetch_simkl():
        if is_enabled('provider_simkl'):
            # simkl_id mapping not strictly passed, maybe add later
            return ('simkl', [])
        return ('simkl', [])

    def fetch_filler():
        if is_enabled('enable_filler') and title_eng:
            return ('filler', anime_filler.get_filler_data(title_eng))
        return ('filler', [])

    logger(f"Fetching episode metadata from providers for MAL ID: {mal_id}", level="INFO")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_anizip),
            executor.submit(fetch_jikan),
            executor.submit(fetch_kitsu),
            executor.submit(fetch_simkl),
            executor.submit(fetch_filler)
        ]

        for future in concurrent.futures.as_completed(futures):
            provider, data = future.result()
            meta_cache[provider] = data

    # Base list is anizip if available, else fallback to tvdb
    final_episodes = []
    
    anizip_data = meta_cache.get('anizip')
    jikan_data = meta_cache.get('jikan')
    filler_data = meta_cache.get('filler')
    
    if anizip_data and anizip_data.get('episodes'):
        # AniZip provides episodes
        for ep_num, ep_data in anizip_data['episodes'].items():
            if not ep_num.isdigit(): continue
            
            # Map AniZip fields to our expected format
            season = ep_data.get('seasonNumber', 1)
            episode = int(ep_num)
            
            # Get preferred title language setting
            val = str(ADDON.getSetting('indexer_title_language')).lower()
            title_language = val if val else 'english'
            
            # Use Jikan for plots if available, else AniZip
            jikan_ep = next((e for e in jikan_data if str(e.get('mal_id')) == ep_num), None)
            plot = jikan_ep.get('synopsis') if jikan_ep and jikan_ep.get('synopsis') else ep_data.get('overview', '')
            
            # AniZip title mapping ('en' = English, 'x-jat' = Romaji)
            az_titles = ep_data.get('title', {})
            az_eng = az_titles.get('en')
            az_rom = az_titles.get('x-jat')
            
            jikan_title = jikan_ep.get('title') if jikan_ep else None
            jikan_rom = jikan_ep.get('title_romanji') if jikan_ep else None
            
            eng_ep = az_eng or jikan_title
            rom_ep = az_rom or jikan_rom or jikan_title
            
            if title_language == 'english':
                title = eng_ep or rom_ep or f'Episode {episode}'
            else:
                title = rom_ep or eng_ep or f'Episode {episode}'
                
            aired = jikan_ep.get('aired') if jikan_ep and jikan_ep.get('aired') else ep_data.get('airDate', '')
            
            # Check filler
            if filler_data and len(filler_data) >= episode:
                if 'Filler' in filler_data[episode - 1]:
                    title = f"[Filler] {title}"
            
            # Get episode image if available
            image = ep_data.get('image', '')
            
            final_episodes.append({
                'title': title,
                'plot': plot,
                'aired': aired[:10] if aired else '',
                'season': season,
                'episode': episode,
                'absolute_number': episode,
                'image': image
            })
    else:
        # TVDB Fallback
        if ADDON.getSetting('provider_tvdb') == 'true' and tvdb_id:
            tvdb_eps = tvdb.get_series_episodes_api(tvdb_id)
            if tvdb_eps:
                for ep in tvdb_eps:
                    season = ep.get('airedSeason', 1)
                    episode = ep.get('airedEpisodeNumber', 1)
                    abs_num = ep.get('absoluteNumber', episode)
                    
                    title = ep.get('episodeName', f'Episode {episode}')
                    
                    if filler_data and len(filler_data) >= abs_num:
                        if 'Filler' in filler_data[abs_num - 1]:
                            title = f"[Filler] {title}"

                    final_episodes.append({
                        'title': title,
                        'plot': ep.get('overview', ''),
                        'aired': ep.get('firstAired', ''),
                        'season': season,
                        'episode': episode,
                        'absolute_number': abs_num,
                        'tvdb_id': ep.get('id'),
                        'image': ep.get('image', '')
                    })
                    
    # Cache results for 24 hours
    set_cache(cache_key, final_episodes, expiry_hours=24)
    return final_episodes

def get_cached_episode(mal_id, season, episode):
    cache_key = f"episode_meta_{mal_id}"
    episodes = get_cache(cache_key)
    if episodes:
        for ep in episodes:
            if int(ep.get('season', 1)) == int(season) and int(ep.get('episode', 1)) == int(episode):
                return ep
    return None
