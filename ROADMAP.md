This is a great idea. When building a complex Kodi scraper—especially for anime, where metadata is famously fractured across different numbering conventions (Absolute vs. Season/Episode)—stepping back to define the architecture and roadmap is crucial.

Based on the files, the `anime_mappings.db` database, and the bug fixes we've pushed so far, here is the updated **Project Plan and Goals** for `metadata.anime.otaku.python`.

---

# 🚀 Project Plan: Anime Metadata Indexer (Otaku Python)

**Repository:** `RPDevs-Builds/metadata.anime.otaku.python`  
**Goal:** Create a robust, multi-API Kodi metadata scraper that accurately indexes anime by bridging Eastern trackers (AniList, MAL) with Western standard formats (TVDB, TMDB) using a local SQLite mapping database.

## 🎯 High-Level Project Goals

1. **Accurate Anime Scraping:** Solve the "Anime Season" problem by translating absolute episode numbers (AniList/MAL) into Kodi-friendly TV Show Seasons/Episodes (TVDB/TMDB) using `anime_mappings.db`.
2. **Kodi API Compliance:** Strictly adhere to Kodi's Python Scraper framework (`action=find`, `getdetails`, `getepisodelist`, `getepisodedetails`) so the `VideoInfoScanner` cleanly adds files to the user's library.
3. **Rich Metadata:** Pull in high-quality localized metadata, character data, ratings (IMDb, Trakt, MAL), and extended artwork.
4. **Automated CI/CD:** Maintain a GitHub Actions pipeline that automatically lints, packages, and releases the addon as an installable `.zip` file.

---

## 🗺️ Development Roadmap

### Phase 1: Core Foundation & Stability (⚡ *Completed*)

*Focus: Getting Kodi to successfully communicate with the addon without throwing C++ or Directory errors.*

* [x] Scaffold basic plugin structure and router (`actions.py`, `main.py`).
* [x] Fix `sys.argv` query string parsing using `urllib.parse`.
* [x] Implement proper Kodi directory lifecycles (`xbmcplugin.addDirectoryItem` and `endOfDirectory`).
* [x] Ensure `?action=find` successfully returns search results.
* [x] Stabilize `?action=getdetails` and `?action=getepisodelist` so Kodi's VideoInfoScanner successfully indexes local `.mkv` files into the database.
* [x] Wire up the local `anime_mappings.db` to translate IDs (e.g., getting a `tvdb_id` from an `anilist_id`).

### Phase 2: Metadata Providers & Data Enrichment (⚡ *Completed / Integrated*)

*Focus: Fetching the actual show data from the internet while keeping Kodi sandbox-friendly.*

* [x] **AniList API (`anilist.py`):** GraphQL query for primary show info, synopses, and genres. (Implemented via standard `urllib.request`)
* [x] **TVDB/TMDB APIs (`tvdb.py`, `tmdb.py`):** Fetch season/episode structures and exact broadcast dates. (Implemented via standard `urllib.request`)
* [/] **Artwork Engine (`artwork.py`):** Aggregate posters, fanart, and banners. (MAPPED: Currently using AniList/TMDB primary artwork directly. Advanced Fanart.tv integration remains a future polish item.)
* [x] **Ratings Engine (`ratings.py`):** Implement fallback ratings (e.g., try MAL, fallback to Trakt, fallback to IMDb). (MAPPED: Implemented multi-provider rating fallback chain with primary/secondary score settings.)

### Phase 3: Edge Cases & Advanced Features (📍 *We are currently here*)

*Focus: Handling weird anime setups and local user overrides.*

* [x] **NFO Parsing (`nfo.py`):** Allow the scraper to read local `.nfo` files to explicitly set an AniList or TVDB ID, bypassing the search phase.
* [ ] **Formatting Logic (`episodes.py`):** Handle Anime Movies vs. OVAs vs. TV Shows accurately.
* [x] **Settings Integration (`settings.xml`):** Ensure user preferences (e.g., enabling/disabling specific providers, configuring custom API keys) actively modify the scraping logic.

### Phase 4: Polish, Optimization & Release (⚡ *Completed*)

*Focus: Making it production-ready and standard-compliant.*

* [x] **Caching (`database.py` / `database_sync.py`):** SQLite database caching for all compiled episode lists for 24 hours to prevent rate-limiting and accelerate library refreshes.
* [x] **Code Cleanup & Sandbox Compliance:** Removed external third-party dependencies (`requests`, `beautifulsoup4`) in favor of pure standard library `urllib` and `json` to run flawlessly inside Kodi's sandbox.
* [x] **CI/CD Pipeline**: Configured a robust release workflow, resolved recursive bot-commit loops, and established automatic tag-triggered zip builds.

---

## 🛠️ Next Steps for Us

To proceed with Phase 3 and improve overall scraper reliability:

1. **Ratings Engine (`ratings.py`)**: Implement fallback ratings (e.g., try MAL, fallback to Trakt, fallback to IMDb).
2. **Artwork Polish**: Incorporate additional artwork fallback engines (Fanart.tv).
3. **Formatting Logic (`episodes.py`)**: Handle Anime Movies vs. OVAs vs. TV Shows accurately.
