# -*- coding: utf-8 -*-
import sys
from resources.lib import actions
from resources.lib.utils import logger

if __name__ == '__main__':
    # sys.argv[2] contains the full query string (e.g. "?action=find&title=...")
    query_string = sys.argv[2]
    logger(f"Kodi requested scraper action: {query_string}")
    
    try:
        actions.router(query_string, sys.argv)
    except Exception as e:
        logger(f"Scraper Exception: {e}", level="ERROR")
