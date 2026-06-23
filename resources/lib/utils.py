import xbmc
import os
import datetime

ADDON = None
try:
    import xbmcaddon
    ADDON = xbmcaddon.Addon('metadata.anime.otaku.python')
except:
    pass

def get_setting(key, default=""):
    if ADDON:
        return ADDON.getSetting(key) or default
    return default

def logger(message, level="INFO"):
    """
    Writes messages directly to kodi.log and optionally to a custom log file.
    Levels: DEBUG, INFO, WARNING, ERROR
    """
    level_priorities = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40
    }
    
    kodi_levels = {
        "INFO": xbmc.LOGINFO,
        "WARNING": xbmc.LOGWARNING,
        "ERROR": xbmc.LOGERROR,
        "DEBUG": xbmc.LOGDEBUG
    }
    
    configured_level_str = get_setting('debug_level', 'INFO')
    configured_level = level_priorities.get(configured_level_str, 20)
    message_level = level_priorities.get(level, 20)
    
    if message_level < configured_level:
        return
        
    log_message = f"[OTAKU SCRAPER] {message}"
    
    try:
        xbmc.log(log_message, kodi_levels.get(level, xbmc.LOGDEBUG))
    except:
        pass
        
    custom_path = get_setting('custom_log_path')
    if custom_path and os.path.isdir(custom_path):
        log_file = os.path.join(custom_path, 'otaku_scraper.log')
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except:
            pass
