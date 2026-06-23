# -*- coding: utf-8 -*-
import sys
import os

# Append the project path to sys.path so we can import from resources.lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Kodi modules before importing resources.lib.movies
class MockXBMC:
    LOGINFO = 1
    LOGWARNING = 2
    LOGERROR = 3
    LOGDEBUG = 0
    Actor = lambda self, name, role: (name, role)
    def log(self, msg, level=0):
        print(f"[KODI LOG {level}] {msg}")
sys.modules['xbmc'] = MockXBMC()

class MockXBMCAddon:
    class Addon:
        def __init__(self, id=None):
            self.id = id
        def getAddonInfo(self, info_type):
            if info_type == 'path':
                return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            return ''
        def getSetting(self, setting_id):
            if setting_id == 'indexer_title_language':
                return 'english'
            return ''
        def getSettingBool(self, setting_id):
            return True
sys.modules['xbmcaddon'] = MockXBMCAddon()

class MockXBMCVFS:
    def translatePath(self, path):
        return path
sys.modules['xbmcvfs'] = MockXBMCVFS()

class MockXBMCGUI:
    class ListItem:
        def __init__(self, label="", offscreen=False):
            self.label = label
            self.info = {}
            self.art = {}
            self.available_artwork = []
        def setInfo(self, type, info):
            self.info.update(info)
        def setArt(self, art):
            self.art = art
        def addAvailableArtwork(self, art, art_type):
            self.available_artwork.append((art, art_type))
        def getVideoInfoTag(self):
            return self
        def setTitle(self, title): self.info['title'] = title
        def setPlot(self, plot): self.info['plot'] = plot
        def setGenres(self, genres): self.info['genre'] = genres
        def setStudios(self, studios): self.info['studios'] = studios
        def setMediaType(self, mediatype): self.info['mediatype'] = mediatype
        def setYear(self, year): self.info['year'] = year
        def setPremiered(self, premiered): self.info['premiered'] = premiered
        def setUniqueIDs(self, ids, default): self.info['unique_ids'] = ids
        def setRating(self, rating, votes, rating_type, primary):
            self.info[f'rating_{rating_type}'] = (rating, votes)
        def setCast(self, cast): self.info['cast'] = cast
        def setTrailer(self, trailer): self.info['trailer'] = trailer
sys.modules['xbmcgui'] = MockXBMCGUI()

class MockXBMCPlugin:
    def addDirectoryItem(self, handle, url, listitem, isFolder):
        print(f"  [DirectoryItem] URL: {url} | Label: {listitem.label} | isFolder: {isFolder}")
    def endOfDirectory(self, handle):
        print("  [EndOfDirectory]")
    def setResolvedUrl(self, handle, succeeded, listitem):
        print(f"  [ResolvedUrl] Succeeded: {succeeded} | Label: {listitem.label}")
        print(f"  Info dict: {listitem.info}")
        print(f"  Art dict: {listitem.art}")
sys.modules['xbmcplugin'] = MockXBMCPlugin()

from resources.lib.movies import search_movies_anilist, find_movie, get_movie_details

if __name__ == '__main__':
    print("Testing search_movies_anilist...")
    movies = search_movies_anilist("Your Name")
    print(f"Found {len(movies)} results:")
    for m in movies:
        print(f" - ID: {m['id']} | Title: {m['title']} | Format: {m['format']}")
        
    print("\nTesting find_movie...")
    find_movie(1, "Your Name")
    
    print("\nTesting get_movie_details...")
    # Use AniList ID for Your Name (21519)
    get_movie_details(1, "anilist_id=21519")
