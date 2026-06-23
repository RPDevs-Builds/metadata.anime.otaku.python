# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcplugin
import xbmcgui
import urllib.parse
from .db_connector import get_mapping
from .providers import anilist, tvdb, tmdb, simkl
from .metadata_engine import fetch_all_metadata, get_cached_episode
from .database_sync import init_db
from .utils import logger
import os
import shutil
import xml.etree.ElementTree as ET
try:
    import xbmcvfs
except ImportError:
    pass

# Initialize local SQLite cache schema
init_db()

def router(query_string, args, mode='tvshow'):
    handle = int(args[1])
    
    if query_string.startswith('?'):
        query_string = query_string[1:]
    
    params = urllib.parse.parse_qs(query_string)
    action = params.get('action', [''])[0]
    
    if action == 'find':
        title = params.get('title', [''])[0]
        if mode == 'movie':
            from .movies import find_movie
            find_movie(handle, title)
        else:
            find_show(handle, title)
    elif action == 'nfourl':
        nfo_text = params.get('nfo', [''])[0]
        from .nfo import parse_nfo_and_search
        parse_nfo_and_search(handle, nfo_text)
    elif action == 'getdetails':
        url = params.get('url', [''])[0]
        if mode == 'movie':
            from .movies import get_movie_details
            get_movie_details(handle, url)
        else:
            get_series_details(handle, url)
    elif action == 'getepisodelist':
        url = params.get('url', [''])[0]
        get_episode_list(handle, url)
    elif action == 'getepisodedetails':
        url = params.get('url', [''])[0]
        get_episode_details(handle, url)
    elif action == 'getartwork':
        anime_id = params.get('id', [''])[0]
        get_artwork(handle, anime_id)
    elif action == 'backup_settings':
        backup_settings()
    elif action == 'restore_settings':
        restore_settings()

def get_profile_path():
    try:
        addon = xbmcaddon.Addon('metadata.anime.otaku.python')
        if hasattr(xbmcvfs, 'translatePath'):
            return xbmcvfs.translatePath(addon.getAddonInfo('profile'))
        else:
            return xbmc.translatePath(addon.getAddonInfo('profile'))
    except:
        return ''

def backup_settings():
    profile_dir = get_profile_path()
    if not profile_dir:
        xbmcgui.Dialog().notification('Otaku Backup', 'Failed to locate profile directory', xbmcgui.NOTIFICATION_ERROR)
        return
        
    settings_file = os.path.join(profile_dir, 'settings.xml')
    backup_file = os.path.join(profile_dir, 'settings_backup.xml')
    
    if os.path.exists(settings_file):
        try:
            shutil.copy2(settings_file, backup_file)
            xbmcgui.Dialog().notification('Otaku Backup', 'Settings successfully backed up!', xbmcgui.NOTIFICATION_INFO)
            logger("Settings backed up successfully.", level="INFO")
        except Exception as e:
            logger(f"Settings backup failed: {e}", level="ERROR")
            xbmcgui.Dialog().notification('Otaku Backup', f'Backup failed: {e}', xbmcgui.NOTIFICATION_ERROR)
    else:
        xbmcgui.Dialog().notification('Otaku Backup', 'No settings.xml found to backup', xbmcgui.NOTIFICATION_WARNING)

def restore_settings():
    profile_dir = get_profile_path()
    if not profile_dir:
        return
        
    backup_file = os.path.join(profile_dir, 'settings_backup.xml')
    
    if os.path.exists(backup_file):
        confirm = xbmcgui.Dialog().yesno('Otaku Restore', 'Restore settings from the last backup?\nThis will overwrite your current configuration.')
        if confirm:
            try:
                addon = xbmcaddon.Addon('metadata.anime.otaku.python')
                tree = ET.parse(backup_file)
                root = tree.getroot()
                
                count = 0
                for setting in root.iter('setting'):
                    setting_id = setting.get('id')
                    setting_value = setting.text if setting.text else ""
                    if setting_id:
                        addon.setSetting(setting_id, setting_value)
                        count += 1
                        
                xbmcgui.Dialog().notification('Otaku Restore', f'Restored {count} settings successfully!', xbmcgui.NOTIFICATION_INFO)
                logger(f"Restored {count} settings from backup.", level="INFO")
            except Exception as e:
                logger(f"Settings restore failed: {e}", level="ERROR")
                xbmcgui.Dialog().notification('Otaku Restore', f'Restore failed: {e}', xbmcgui.NOTIFICATION_ERROR)
    else:
        xbmcgui.Dialog().notification('Otaku Restore', 'No backup file found!', xbmcgui.NOTIFICATION_ERROR)

def find_show(handle, title):
    try:
        import xbmcaddon
        title_language = (xbmcaddon.Addon('metadata.anime.otaku.python').getSetting('indexer_title_language') or 'english').lower()
    except ImportError:
        title_language = 'english'

    results = anilist.search_anime(title)
    
    for anime in results:
        mapping = get_mapping(anime['id'], 'anilist_id')
        
        eng_title = anime.get('title', {}).get('english')
        rom_title = anime.get('title', {}).get('romaji')
        
        if title_language == 'english':
            preferred_title = eng_title or rom_title or 'Unknown Anime'
        else:
            preferred_title = rom_title or eng_title or 'Unknown Anime'
        
        if mapping:
            url_params = {
                'anilist_id': mapping.get('anilist_id', ''),
                'mal_id': mapping.get('mal_id', ''),
                'tvdb_id': mapping.get('thetvdb_id', ''),
                'tmdb_id': mapping.get('themoviedb_id', ''),
                'imdb_id': mapping.get('imdb_id', ''),
                'simkl_id': mapping.get('simkl_id', ''),
                'mal_score': mapping.get('score', ''),
                'tvdb_season': mapping.get('thetvdb_season', ''),
                'title_eng': preferred_title
            }
            
            # Clean out any empty/null values and encode
            url_params = {k: v for k, v in url_params.items() if v}
            encoded_url = urllib.parse.urlencode(url_params)
            
            liz = xbmcgui.ListItem(preferred_title, offscreen=True)
            
            xbmcplugin.addDirectoryItem(handle=handle, url=encoded_url, listitem=liz, isFolder=True)
            
    xbmcplugin.endOfDirectory(handle)

def get_series_details(handle, url):
    ids = dict(urllib.parse.parse_qsl(url))
    
    tvdb_id = ids.get('tvdb_id')
    anilist_id = ids.get('anilist_id')
    imdb_id = ids.get('imdb_id')
    tmdb_id = ids.get('tmdb_id')
    simkl_id = ids.get('simkl_id')
    
    tvdb_data = tvdb.get_series_details_api(tvdb_id) if tvdb_id else {}
    anilist_data = anilist.get_anime_details(anilist_id) if anilist_id else {}
    tmdb_data = tmdb.get_series_data(tmdb_id) if tmdb_id else {}
    simkl_data = simkl.get_ratings(simkl_id) if simkl_id else {}
    
    try:
        import xbmcaddon
        addon = xbmcaddon.Addon('metadata.anime.otaku.python')
        title_language = (addon.getSetting('indexer_title_language') or 'english').lower()
        enable_posters = addon.getSettingBool('enable_posters') if addon.getSetting('enable_posters') else True
        enable_banners = addon.getSettingBool('enable_banners') if addon.getSetting('enable_banners') else True
        enable_fanart = addon.getSettingBool('enable_fanart') if addon.getSetting('enable_fanart') else True
        
        # New metadata preferences
        rating_source = addon.getSetting('rating_source') or 'AniList'
        enable_anilist_rating = addon.getSettingBool('enable_anilist_rating') if addon.getSetting('enable_anilist_rating') else True
        enable_mal_rating = addon.getSettingBool('enable_mal_rating') if addon.getSetting('enable_mal_rating') else True
        enable_tmdb_rating = addon.getSettingBool('enable_tmdb_rating') if addon.getSetting('enable_tmdb_rating') else True
        enable_simkl_rating = addon.getSettingBool('enable_simkl_rating') if addon.getSetting('enable_simkl_rating') else True
        
        plot_source = addon.getSetting('plot_source') or 'AniList'
        release_date_source = addon.getSetting('release_date_source') or 'AniList'
        
        fetch_trailers = addon.getSettingBool('fetch_trailers') if addon.getSetting('fetch_trailers') else True
        fetch_cast = addon.getSettingBool('fetch_cast') if addon.getSetting('fetch_cast') else True
    except ImportError:
        title_language = 'english'
        enable_posters = True
        enable_banners = True
        enable_fanart = True
        rating_source = 'AniList'
        enable_anilist_rating = True
        enable_mal_rating = True
        enable_tmdb_rating = True
        enable_simkl_rating = True
        plot_source = 'AniList'
        release_date_source = 'AniList'
        fetch_trailers = True
        fetch_cast = True
        
    eng_title = anilist_data.get('title', {}).get('english')
    rom_title = anilist_data.get('title', {}).get('romaji')
    
    if title_language == 'english':
        title = eng_title or rom_title or 'Unknown Anime'
    else:
        title = rom_title or eng_title or 'Unknown Anime'
             
    liz = xbmcgui.ListItem(title, offscreen=True)
    
    unique_ids = {}
    if tvdb_id: unique_ids['tvdb'] = str(tvdb_id)
    if imdb_id: unique_ids['imdb'] = str(imdb_id)
    if tmdb_id: unique_ids['tmdb'] = str(tmdb_id)
    if anilist_id: unique_ids['anilist'] = str(anilist_id)
    if ids.get('mal_id'): unique_ids['mal_id'] = str(ids.get('mal_id'))
    if simkl_id: unique_ids['simkl_id'] = str(simkl_id)
    
    # Resolve plot/overview preference
    plot = anilist_data.get('description', '')
    if plot_source == 'TMDb' and tmdb_data.get('overview'):
        plot = tmdb_data['overview']
    elif plot_source == 'TVDB' and tvdb_data.get('overview'):
        plot = tvdb_data['overview']
        
    # Resolve release date preference
    premiered = anilist_data.get('premiered', '')
    if release_date_source == 'TMDb' and tmdb_data.get('first_air_date'):
        premiered = tmdb_data['first_air_date']
    elif release_date_source == 'TVDB' and tvdb_data.get('firstAired'):
        premiered = tvdb_data['firstAired']
        
    # Parse scores
    anilist_score = float(anilist_data.get('average_score', 0) or 0) / 10.0
    
    mal_score_str = ids.get('mal_score')
    mal_score = float(mal_score_str) if mal_score_str else 0.0
    
    tmdb_score = float(tmdb_data.get('siteRating', 0.0) or 0.0)
    tmdb_votes = int(tmdb_data.get('votes', 0) or 0)
    
    simkl_score = float(simkl_data.get('simkl', {}).get('rating', 0.0) or 0.0)
    simkl_votes = int(simkl_data.get('simkl', {}).get('votes', 0) or 0)
    
    # Resolve primary rating and votes
    primary_rating = 0.0
    primary_votes = 0
    primary_rating_type = rating_source.lower()
    
    if rating_source == 'AniList' and anilist_score > 0:
        primary_rating = anilist_score
    elif rating_source == 'MyAnimeList' and mal_score > 0:
        primary_rating = mal_score
        primary_rating_type = 'mal'
    elif rating_source == 'TMDb' and tmdb_score > 0:
        primary_rating = tmdb_score
        primary_votes = tmdb_votes
        primary_rating_type = 'tmdb'
    elif rating_source == 'Simkl' and simkl_score > 0:
        primary_rating = simkl_score
        primary_votes = simkl_votes
        primary_rating_type = 'simkl'
        
    # Fallback rating cascade
    if primary_rating == 0.0:
        if anilist_score > 0:
            primary_rating = anilist_score
            primary_rating_type = 'anilist'
        elif mal_score > 0:
            primary_rating = mal_score
            primary_rating_type = 'mal'
        elif tmdb_score > 0:
            primary_rating = tmdb_score
            primary_votes = tmdb_votes
            primary_rating_type = 'tmdb'
        elif simkl_score > 0:
            primary_rating = simkl_score
            primary_votes = simkl_votes
            primary_rating_type = 'simkl'
            
    # Backward compatibility metadata
    info_dict = {
        'title': title,
        'tvshowtitle': title,
        'plot': plot,
        'genre': anilist_data.get('genres', []),
        'studio': anilist_data.get('studio', ''),
        'status': tvdb_data.get('status', 'Continuing'),
        'premiered': premiered,
        'rating': primary_rating,
        'votes': primary_votes,
        'mediatype': 'tvshow',
        'episodeguide': urllib.parse.quote(url)
    }
    
    # Cast legacy list formatting
    if fetch_cast and anilist_data.get('characters'):
        cast_list = []
        for char in anilist_data['characters']:
            cast_list.append((char['name'], char['role']))
        info_dict['cast'] = cast_list
        
    if fetch_trailers and anilist_data.get('trailer_site') == 'youtube' and anilist_data.get('trailer_id'):
        info_dict['trailer'] = f"plugin://plugin.video.youtube/play/?video_id={anilist_data['trailer_id']}"
    
    year = anilist_data.get('year')
    if year:
        info_dict['year'] = int(year)
        
    liz.setInfo('video', info_dict)
    
    # Artwork mapping
    poster = anilist_data.get('poster')
    banner = anilist_data.get('banner')
    
    art_dict = {}
    if poster and enable_posters:
        art_dict['poster'] = poster
        liz.addAvailableArtwork(poster, 'poster')
    if banner:
        if enable_banners:
            art_dict['banner'] = banner
            liz.addAvailableArtwork(banner, 'banner')
        if enable_fanart:
            art_dict['fanart'] = banner
            liz.addAvailableArtwork(banner, 'fanart')
            
    if art_dict:
        liz.setArt(art_dict)
        
    # Modern InfoTagVideo mapping (Kodi 20+)
    try:
        vtag = liz.getVideoInfoTag()
        vtag.setTitle(title)
        vtag.setTvShowTitle(title)
        vtag.setPlot(plot)
        vtag.setGenres(anilist_data.get('genres', []))
        vtag.setStudios([anilist_data.get('studio', '')] if anilist_data.get('studio') else [])
        vtag.setTvShowStatus(tvdb_data.get('status', 'Continuing'))
        vtag.setMediaType('tvshow')
        if year:
            vtag.setYear(int(year))
        if premiered:
            vtag.setPremiered(premiered)
        vtag.setEpisodeGuide(urllib.parse.quote(url))
        vtag.setUniqueIDs(unique_ids, 'mal_id' if 'mal_id' in unique_ids else 'tvdb')
        
        # Inject primary rating
        if primary_rating > 0:
            vtag.setRating(primary_rating, primary_votes, primary_rating_type, True)
            
        # Additional ratings if enabled
        if enable_anilist_rating and anilist_score > 0:
            vtag.setRating(anilist_score, 0, 'anilist', primary_rating_type == 'anilist')
        if enable_mal_rating and mal_score > 0:
            vtag.setRating(mal_score, 0, 'mal', primary_rating_type == 'mal')
        if enable_tmdb_rating and tmdb_score > 0:
            vtag.setRating(tmdb_score, tmdb_votes, 'tmdb', primary_rating_type == 'tmdb')
        if enable_simkl_rating and simkl_score > 0:
            vtag.setRating(simkl_score, simkl_votes, 'simkl', primary_rating_type == 'simkl')
        
        if fetch_cast and anilist_data.get('characters'):
            vtag.setCast([xbmc.Actor(char['name'], char['role']) for char in anilist_data['characters']])
            
        if fetch_trailers and anilist_data.get('trailer_site') == 'youtube' and anilist_data.get('trailer_id'):
            vtag.setTrailer(f"plugin://plugin.video.youtube/play/?video_id={anilist_data['trailer_id']}")
        
        if poster and enable_posters:
            vtag.addAvailableArtwork(poster, 'poster')
        if banner:
            if enable_banners:
                vtag.addAvailableArtwork(banner, 'banner')
            if enable_fanart:
                vtag.addAvailableArtwork(banner, 'fanart')
    except Exception as e:
        logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
        
    liz.setUniqueIDs(unique_ids, 'mal_id' if 'mal_id' in unique_ids else 'tvdb')
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)

def get_episode_list(handle, url):
    ids = dict(urllib.parse.parse_qsl(urllib.parse.unquote(url)))
    mal_id = ids.get('mal_id')
    tvdb_id = ids.get('tvdb_id')
    title_eng = ids.get('title_eng')
    
    if not mal_id and not tvdb_id:
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return
        
    episodes = fetch_all_metadata(mal_id, tvdb_id, title_eng)
    if not episodes:
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return
        
    last_liz = None
    for ep in episodes:
        title = ep.get('title', 'Episode')
        liz = xbmcgui.ListItem(title, offscreen=True)
        
        # Backward compatibility details
        details = {
            'title': title,
            'plot': ep.get('plot', ''),
            'aired': ep.get('aired', ''),
            'premiered': ep.get('aired', ''),
            'season': ep.get('season', 1),
            'episode': ep.get('episode', 1),
            'mediatype': 'episode'
        }
        liz.setInfo('video', details)
        
        image = ep.get('image', '')
        if image:
            liz.addAvailableArtwork(image, 'thumb')
            liz.setArt({'thumb': image})
            
        # Modern InfoTagVideo mapping (Kodi 20+)
        try:
            vtag = liz.getVideoInfoTag()
            vtag.setTitle(title)
            vtag.setSeason(int(ep.get('season', 1)))
            vtag.setEpisode(int(ep.get('episode', 1)))
            vtag.setMediaType('episode')
            if ep.get('plot'):
                vtag.setPlot(ep.get('plot'))
            if ep.get('aired'):
                vtag.setFirstAired(ep.get('aired'))
                vtag.setPremiered(ep.get('aired'))
            if image:
                vtag.addAvailableArtwork(image, 'thumb')
        except Exception as e:
            logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
            
        # Build episode url to pass required identifiers for details phase
        ep_url = urllib.parse.urlencode({
            'mal_id': mal_id,
            'season': ep.get('season', 1),
            'episode': ep.get('episode', 1),
            'tvdb_id': ep.get('tvdb_id', '')
        })
        xbmcplugin.addDirectoryItem(handle=handle, url=ep_url, listitem=liz, isFolder=True)
        last_liz = liz
        
    if last_liz:
        try:
            xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=last_liz)
        except Exception:
            pass
            
    xbmcplugin.endOfDirectory(handle)

def get_episode_details(handle, url):
    params = dict(urllib.parse.parse_qsl(url))
    mal_id = params.get('mal_id')
    season = params.get('season')
    episode = params.get('episode')
    
    if not mal_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    # Read from local SQLite cache instead of fetching again!
    ep = get_cached_episode(mal_id, season, episode)
    
    if not ep:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    title = ep.get('title', 'Episode')
    liz = xbmcgui.ListItem(title, offscreen=True)
    
    unique_ids = {}
    if params.get('tvdb_id'): unique_ids['tvdb'] = str(params.get('tvdb_id'))
    unique_ids['mal_id'] = str(mal_id)
    
    # Backward compatibility details - CRITICAL for Kodi scrapers
    details = {
        'title': title,
        'plot': ep.get('plot', ''),
        'aired': ep.get('aired', ''),
        'premiered': ep.get('aired', ''),
        'season': int(ep.get('season', 1)),
        'episode': int(ep.get('episode', 1)),
        'mediatype': 'episode'
    }
    liz.setInfo('video', details)
    
    try:
        import xbmcaddon
        enable_fanart = xbmcaddon.Addon('metadata.anime.otaku.python').getSettingBool('enable_fanart') if xbmcaddon.Addon('metadata.anime.otaku.python').getSetting('enable_fanart') else True
    except ImportError:
        enable_fanart = True
        
    image = ep.get('image', '')
    if image and enable_fanart:
        liz.addAvailableArtwork(image, 'thumb')
        liz.setArt({'thumb': image})
    
    # Modern InfoTagVideo mapping (Kodi 20+)
    try:
        vtag = liz.getVideoInfoTag()
        vtag.setTitle(title)
        vtag.setSeason(int(ep.get('season', 1)))
        vtag.setEpisode(int(ep.get('episode', 1)))
        vtag.setMediaType('episode')
        if ep.get('plot'):
            vtag.setPlot(ep.get('plot'))
        if ep.get('aired'):
            vtag.setFirstAired(ep.get('aired'))
            vtag.setPremiered(ep.get('aired'))
        if image and enable_fanart:
            vtag.addAvailableArtwork(image, 'thumb')
        vtag.setUniqueIDs(unique_ids, 'mal_id')
    except Exception as e:
        logger(f"Error setting VideoInfoTag: {e}", level="WARNING")
        
    liz.setUniqueIDs(unique_ids, 'mal_id')
    
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)

def get_artwork(handle, anime_id):
    logger(f"Get Artwork request for ID: {anime_id}")
    if not anime_id:
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem(offscreen=True))
        return
        
    # Map MAL ID / default ID to AniList ID if needed
    mapping = get_mapping(anime_id, 'mal_id')
    anilist_id = mapping.get('anilist_id') if mapping else anime_id
    
    anilist_data = anilist.get_anime_details(anilist_id) if anilist_id else {}
    
    liz = xbmcgui.ListItem(str(anime_id), offscreen=True)
    
    poster = anilist_data.get('poster')
    banner = anilist_data.get('banner')
    
    art_dict = {}
    if poster:
        art_dict['poster'] = poster
        liz.addAvailableArtwork(poster, 'poster')
    if banner:
        art_dict['banner'] = banner
        art_dict['fanart'] = banner
        liz.addAvailableArtwork(banner, 'banner')
        liz.addAvailableArtwork(banner, 'fanart')
    if art_dict:
        liz.setArt(art_dict)
        
    try:
        vtag = liz.getVideoInfoTag()
        if poster:
            vtag.addAvailableArtwork(poster, 'poster')
        if banner:
            vtag.addAvailableArtwork(banner, 'banner')
            vtag.addAvailableArtwork(banner, 'fanart')
    except Exception as e:
        logger(f"Error setting VideoInfoTag artwork: {e}", level="WARNING")
        
    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=liz)
