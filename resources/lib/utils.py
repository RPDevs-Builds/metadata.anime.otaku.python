import xbmc

def logger(message, level="INFO"):
    """
    Writes messages directly to kodi.log for debugging.
    Levels: INFO, WARNING, ERROR, DEBUG
    """
    levels = {
        "INFO": xbmc.LOGINFO,
        "WARNING": xbmc.LOGWARNING,
        "ERROR": xbmc.LOGERROR,
        "DEBUG": xbmc.LOGDEBUG
    }
    
    # Prefix the message so you can easily CTRL+F for it in the log
    log_message = f"[OTAKU SCRAPER] {message}"
    xbmc.log(log_message, levels.get(level, xbmc.LOGDEBUG))
