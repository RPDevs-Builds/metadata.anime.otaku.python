# -*- coding: utf-8 -*-
import sys
from resources.lib import actions
from resources.lib.utils import logger

if __name__ == '__main__':
    query_string = sys.argv[2]
    logger(f"Kodi requested movie scraper action: {query_string}")
    
    try:
        actions.router(query_string, sys.argv, mode='movie')
    except Exception as e:
        logger(f"Movie Scraper Exception: {e}", level="ERROR")
