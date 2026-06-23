# -*- coding: utf-8 -*-
import os
import shutil
import time
import requests
import xbmcaddon
import xbmcvfs
from .utils import logger

MAPPINGS_URL = "https://github.com/Goldenfreddy0703/Otaku-Mappings/raw/refs/heads/main/anime_mappings.db"

def run_sync_check():
    """
    Triggers chronological delta checks against add-on initialization intervals.
    Downloads tracking updates into native userdata system layers.
    """
    addon = xbmcaddon.Addon('metadata.anime.otaku.python')
    if not addon.getSettingBool('db_auto_update'):
        return

    profile_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    timestamp_file = os.path.join(profile_dir, 'last_update.txt')
    current_time = int(time.time())
    interval_days = addon.getSettingInt('db_update_interval')
    interval_seconds = interval_days * 86400

    should_update = False
    if not os.path.exists(os.path.join(profile_dir, 'anime_mappings.db')):
        should_update = True
    elif os.path.exists(timestamp_file):
        try:
            with open(timestamp_file, 'r') as f:
                last_update = int(f.read().strip())
            if (current_time - last_update) >= interval_seconds:
                should_update = True
        except ValueError:
            should_update = True
    else:
        should_update = True

    if should_update:
        logger("Asynchronous mapping dictionary check validation triggered.")
        _download_mappings(profile_dir, timestamp_file, current_time)

def _download_mappings(target_dir, timestamp_file, current_time):
    temp_db_path = os.path.join(target_dir, 'anime_mappings.db.tmp')
    final_db_path = os.path.join(target_dir, 'anime_mappings.db')
    
    try:
        response = requests.get(MAPPINGS_URL, stream=True, timeout=20)
        response.raise_for_status()
        
        with open(temp_db_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        if os.path.exists(final_db_path):
            os.remove(final_db_path)
            
        shutil.move(temp_db_path, final_db_path)
        
        with open(timestamp_file, 'w') as f:
            f.write(str(current_time))
            
        logger("Mapping persistence catalog safely swapped to active userdata profile.")
    except Exception as e:
        logger(f"Network processing mirror error: {e}", level="WARNING")
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
