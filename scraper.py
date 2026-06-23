# -*- coding: utf-8 -*-
import sys
from resources.lib import actions
from resources.lib.utils import logger

if __name__ == '__main__':
    # Kodi invokes this script with the action as an argument
    action = sys.argv[2]
    logger(f"Kodi requested scraper action: {action}")
    
    try:
        actions.router(action, sys.argv)
    except Exception as e:
        logger(f"Scraper Exception: {e}", level="ERROR")
