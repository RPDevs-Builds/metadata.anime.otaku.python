#!/usr/bin/env python3
import os
import re
import sys
import sqlite3
import json
import urllib.request
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'lib', 'anime_mappings.db')

def search_local_db(title):
    """Search the local anime_mappings.db for a MAL ID based on folder title."""
    if not os.path.exists(DB_PATH):
        return None, None
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Strip common years and tags from title for better matching
    clean_title = re.sub(r'\(\d{4}\)', '', title).strip()
    clean_title = clean_title.replace('.', ' ').replace('-', ' ').strip()
    
    cursor.execute("SELECT mal_id, mal_title FROM anime WHERE mal_title LIKE ?", (f"%{clean_title}%",))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row['mal_id'], row['mal_title']
    return None, None

def get_anilist_title(mal_id, title_language='english'):
    """Fetch preferred title from AniList GraphQL."""
    query = '''
    query ($id: Int) {
      Media(idMal: $id, type: ANIME) {
        title { romaji english }
      }
    }
    '''
    try:
        req = urllib.request.Request(
            'https://graphql.anilist.co',
            data=json.dumps({'query': query, 'variables': {'id': int(mal_id)}}).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            title_dict = data.get('data', {}).get('Media', {}).get('title', {})
            eng_title = title_dict.get('english')
            rom_title = title_dict.get('romaji')
            if title_language == 'english':
                return eng_title or rom_title
            else:
                return rom_title or eng_title
    except:
        return None

def search_anilist(title, title_language='english'):
    """Fallback to AniList GraphQL search."""
    clean_title = re.sub(r'\(\d{4}\)', '', title).strip()
    query = '''
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        idMal
        title { romaji english }
      }
    }
    '''
    try:
        req = urllib.request.Request(
            'https://graphql.anilist.co',
            data=json.dumps({'query': query, 'variables': {'search': clean_title}}).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            anime = data.get('data', {}).get('Media')
            if anime and anime.get('idMal'):
                eng_title = anime['title'].get('english')
                rom_title = anime['title'].get('romaji')
                if title_language == 'english':
                    pref_title = eng_title or rom_title
                else:
                    pref_title = rom_title or eng_title
                return anime['idMal'], pref_title
    except Exception as e:
        pass
    return None, None

def get_anizip_mappings(mal_id):
    """Fetch exact absolute -> season/episode mappings from AniZip."""
    try:
        req = urllib.request.Request(
            f"https://api.ani.zip/mappings?mal_id={mal_id}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('episodes', {})
    except Exception as e:
        print(f"  ❌ AniZip API Error: {e}")
        return {}

def resolve_anime_identity(path, title_language='english'):
    """Determine the MAL ID and clean title of the show for a given path."""
    path = Path(path).resolve()
    is_season = (
        re.search(r'\b(season|specials|ovas|movies|sp)\b', path.name, re.IGNORECASE) 
        or re.match(r'^S\d+$', path.name, re.IGNORECASE)
    )
    
    # Try resolving based on the directory structure
    if is_season:
        is_season_1 = bool(re.search(r'\b(season\s*0*1|s0*1)\b', path.name, re.IGNORECASE))
        if is_season_1:
            search_title = path.parent.name
        else:
            search_title = f"{path.parent.name} {path.name}"
    else:
        search_title = path.name
        
    mal_id, anime_title = search_local_db(search_title)
    if mal_id:
        pref_title = get_anilist_title(mal_id, title_language)
        if pref_title:
            anime_title = pref_title
        return mal_id, anime_title, is_season
        
    mal_id, anime_title = search_anilist(search_title, title_language)
    if mal_id:
        return mal_id, anime_title, is_season
        
    # If the season folder lookup fails, fallback to using the parent folder title
    if is_season:
        mal_id, anime_title = search_local_db(path.parent.name)
        if not mal_id:
            mal_id, anime_title = search_anilist(path.parent.name, title_language)
        if mal_id:
            pref_title = get_anilist_title(mal_id, title_language)
            if pref_title:
                anime_title = pref_title
            return mal_id, anime_title, is_season

    return None, None, is_season

def get_consolidated_episodes(primary_mal_id, anime_title, is_season):
    """
    Fetch all episode mapping objects for the primary MAL ID and related parts.
    Ensures multi-part split seasons (like AOT Season 3 Part 2) are mapped correctly.
    """
    episodes = []
    seen_ids = set()
    
    # 1. Fetch primary mapping
    primary_map = get_anizip_mappings(primary_mal_id)
    if primary_map:
        for ep_data in primary_map.values():
            ep_id = ep_data.get('tvdbId')
            if ep_id and ep_id not in seen_ids:
                episodes.append(ep_data)
                seen_ids.add(ep_id)
                
    # 2. Check for related parts/specials if it is a season folder
    if is_season:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT mal_title FROM anime WHERE mal_id = ?", (primary_mal_id,))
            primary_row = cursor.fetchone()
            if primary_row:
                db_title = primary_row['mal_title']
                cursor.execute(
                    "SELECT mal_id, mal_title FROM anime WHERE mal_title LIKE ? AND mal_id != ?", 
                    (f"{db_title}%", primary_mal_id)
                )
                rows = cursor.fetchall()
                
                # Check if primary title contains "season"
                primary_has_season = bool(re.search(r'\bseason\b', db_title, re.IGNORECASE))
                
                for row in rows:
                    related_title = row['mal_title']
                    related_has_season = bool(re.search(r'\bseason\b', related_title, re.IGNORECASE))
                    # Prevent crossing seasons if the primary wasn't a season (e.g. S1 matching S2)
                    if not primary_has_season and related_has_season:
                        continue
                        
                    print(f"  🔗 Found related part: {related_title} (MAL ID: {row['mal_id']})")
                    related_map = get_anizip_mappings(row['mal_id'])
                    if related_map:
                        for ep_data in related_map.values():
                            ep_id = ep_data.get('tvdbId')
                            if ep_id and ep_id not in seen_ids:
                                episodes.append(ep_data)
                                seen_ids.add(ep_id)
            conn.close()
                            
    return episodes

def find_episode_data(episodes_list, num_str):
    """Search for episode number or absolute episode number match in consolidated mapping list."""
    if not episodes_list:
        return None
    try:
        num = int(num_str)
        for ep_data in episodes_list:
            if ep_data.get('episodeNumber') == num:
                return ep_data
            if ep_data.get('absoluteEpisodeNumber') == num:
                return ep_data
    except ValueError:
        pass
    return None

def clean_show_title_from_filename(filename, anime_title, folder_name, parent_name=None):
    """Strip show/season title prefixes from filename to avoid matching year/colliding numbers."""
    fn = filename.lower()
    
    def normalize_str(s):
        if not s:
            return ""
        s_clean = re.sub(r'\(\d{4}\)', '', s).strip()
        s_clean = re.sub(r'[._\-;!]', ' ', s_clean)
        return ' '.join(s_clean.split()).lower()
        
    norm_fn = re.sub(r'[._\-;!]', ' ', fn)
    norm_fn = ' '.join(norm_fn.split())
    
    titles_to_remove = [normalize_str(anime_title), normalize_str(folder_name)]
    if parent_name:
        titles_to_remove.append(normalize_str(parent_name))
        
    titles_to_remove = sorted(list(set(t for t in titles_to_remove if t)), key=len, reverse=True)
    
    for title in titles_to_remove:
        if not title:
            continue
        if norm_fn.startswith(title):
            words = title.split()
            escaped_words = [re.escape(w) for w in words]
            pattern = r'^\s*' + r'[\s._\-;!]*'.join(escaped_words) + r'[\s._\-;!]*'
            filename = re.sub(pattern, '', filename, flags=re.IGNORECASE)
            fn = filename.lower()
            norm_fn = re.sub(r'[._\-;!]', ' ', fn)
            norm_fn = ' '.join(norm_fn.split())
            
    return filename

def process_directory(directory, dry_run=True):
    path = Path(directory).resolve()
    if not path.is_dir():
        return
        
    try:
        import xbmcaddon
        title_language = (xbmcaddon.Addon('metadata.anime.otaku.python').getSetting('renamer_title_language') or 'english').lower()
    except ImportError:
        title_language = 'english'

    # Check if there are video files directly in this directory
    has_videos = any(f.suffix.lower() in ['.mkv', '.mp4', '.avi'] for f in path.iterdir() if f.is_file())
    
    if not has_videos:
        subdirs = [d for d in path.iterdir() if d.is_dir()]
        season_dirs = [
            d for d in subdirs 
            if re.search(r'\b(season|specials|ovas|movies|sp)\b', d.name, re.IGNORECASE) 
            or re.match(r'^S\d+$', d.name, re.IGNORECASE)
        ]
        if season_dirs:
            print(f"\n📂 Show directory '{path.name}' has season folders. Processing subfolders...")
            for sdir in season_dirs:
                process_directory(sdir, dry_run=dry_run)
            return
        else:
            print(f"\n📂 Library directory '{path.name}'. Processing all show folders...")
            for subdir in subdirs:
                process_directory(subdir, dry_run=dry_run)
            return

    mal_id, anime_title, is_season = resolve_anime_identity(path, title_language)
    if not mal_id:
        print(f"\n📂 Scanning Directory: {path.name}")
        print("  ❌ Could not identify anime. Skipping.")
        return
        
    print(f"\n📂 Scanning Directory: {path.name}")
    print(f"  ☁️ Identified Anime -> MAL ID: {mal_id} ({anime_title})")

    episodes_list = get_consolidated_episodes(mal_id, anime_title, is_season)
    if not episodes_list:
        print("  ❌ No episode mapping data found on AniZip. Skipping.")
        return

    renames = []
    parent_name = path.parent.name if is_season else None
    
    for file in path.iterdir():
        if file.suffix.lower() not in ['.mkv', '.mp4', '.avi']:
            continue
            
        # Clean title prefix
        temp_name = clean_show_title_from_filename(file.stem, anime_title, path.name, parent_name)
        
        # Strip year, brackets, parens
        temp_name = re.sub(r'\b(19|20)\d{2}\b', '', temp_name)
        temp_name = re.sub(r'\[[^\]]*\]', '', temp_name)
        temp_name = re.sub(r'\([^\)]*\)', '', temp_name)
        
        # Match S01E02 patterns first
        se_match = re.search(r'\bS(\d+)\s*E(\d+)\b', temp_name, re.IGNORECASE)
        if se_match:
            ep_num_str = str(int(se_match.group(2)))
        else:
            match = re.search(r'\b(?:Episode|Ep|E)\s*0*(\d{1,4})\b', temp_name, re.IGNORECASE)
            if not match:
                match = re.search(r'(?:-\s*|_\s*|\s+)0*(\d{1,4})\b', temp_name)
            if match:
                ep_num_str = str(int(match.group(1)))
            else:
                numbers = re.findall(r'\b\d+\b', temp_name)
                if numbers:
                    ep_num_str = str(int(numbers[-1]))
                else:
                    continue
                    
        ep_data = find_episode_data(episodes_list, ep_num_str)
        if ep_data:
            season = ep_data.get('seasonNumber', 1)
            episode = ep_data.get('episodeNumber', int(ep_num_str))
            ep_title = ep_data.get('title', {}).get('en', '')
            
            clean_anime_title = re.sub(r'[\\/*?:"<>|]', "", anime_title)
            # Remove Season suffix from base title if present to avoid duplicating it
            clean_anime_title = re.sub(r'\s+Season\s+\d+', '', clean_anime_title, flags=re.IGNORECASE)
            
            new_name = f"{clean_anime_title} S{season:02d}E{episode:02d}"
            if ep_title:
                clean_ep_title = re.sub(r'[\\/*?:"<>|]', "", ep_title)
                new_name += f" - {clean_ep_title}"
                
            new_name += file.suffix
            new_path = file.with_name(new_name)
            
            if file.name != new_name:
                if new_path.exists():
                    print(f"  ❌ ERROR: Target file {new_name} already exists! Skipping to prevent overwrite.")
                else:
                    renames.append((file, new_path))
                    
    for old_file, new_file in renames:
        if dry_run:
            print(f"  [TEST] {old_file.name} -> {new_file.name}")
        else:
            print(f"  [RENAME] {old_file.name} -> {new_file.name}")
            try:
                os.rename(old_file, new_file)
            except Exception as e:
                print(f"  ❌ Failed to rename {old_file.name}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 otaku_renamer.py <directory> [--execute]")
        sys.exit(1)
        
    target_dir = Path(sys.argv[1])
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("🚀 RUNNING OTAKU RENAMER (DRY RUN - No files will be changed) 🚀")
    else:
        print("⚠️ RUNNING OTAKU RENAMER (EXECUTE MODE - Files WILL be renamed) ⚠️")
        
    process_directory(target_dir, dry_run=dry_run)
