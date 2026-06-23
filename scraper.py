# -*- coding: utf-8 -*-
import sys
from resources.lib import actions
from resources.lib.utils import logger

# Kodi calls this script with specific arguments when it scrapes the library
if __name__ == '__main__':
    # sys.argv[1] contains the Kodi Handle
    # sys.argv[2] contains the action (e.g., 'find', 'getdetails', 'getepisodelist')
    action = sys.argv[2]
    
    logger(f"Kodi requested scraper action: {action}")
    
    try:
        # Route the request into our actions logic
        actions.router(action, sys.argv)
    except Exception as e:
        logger(f"Scraper Failed: {e}", level="ERROR")
