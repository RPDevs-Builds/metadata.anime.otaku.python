This is a great idea. When building a complex Kodi scraper—especially for anime, where metadata is famously fractured across different numbering conventions (Absolute vs. Season/Episode)—stepping back to define the architecture and roadmap is crucial.

Based on the files you've uploaded, the `anime_mappings.db` database, and the bug fixes we've pushed so far, here is a proposed **Project Plan and Goals** for `metadata.anime.otaku.python`.

Review this outline, and let me know what you want to adjust or prioritize!

---

# 🚀 Project Plan: Anime Metadata Indexer (Otaku Python)

**Repository:** `RPDevs-Builds/metadata.anime.otaku.python`
**Goal:** Create a robust, multi-API Kodi metadata scraper that accurately indexes anime by bridging Eastern trackers (AniList, MAL) with Western standard formats (TVDB, TMDB) using a local SQLite mapping database.

## 🎯 High-Level Project Goals

1. **Accurate Anime Scraping:** Solve the "Anime Season" problem by flawlessly translating absolute episode numbers (AniList/MAL) into Kodi-friendly TV Show Seasons/Episodes (TVDB/TMDB) using `anime_mappings.db`.
2. **Kodi API Compliance:** Strictly adhere to Kodi's Python Scraper framework (`action=find`, `getdetails`, `getepisodelist`, `getepisodedetails`) so the `VideoInfoScanner` cleanly adds files to the user's library.
3. **Rich Metadata:** Pull in high-quality localized metadata, character data, ratings (IMDb, Trakt, MAL), and extended artwork (Fanart.tv).
4. **Automated CI/CD:** Maintain a GitHub Actions pipeline that automatically lints, packages, and releases the addon as an installable `.zip` file.

---

## 🗺️ Development Roadmap

### Phase 1: Core Foundation & Stability (📍 *We are currently here*)

*Focus: Getting Kodi to successfully communicate with the addon without throwing C++ or Directory errors.*

* [x] Scaffold basic plugin structure and router (`actions.py`, `main.py`).
* [x] Fix `sys.argv` query string parsing using `urllib.parse`.
* [x] Implement proper Kodi directory lifecycles (`xbmcplugin.addDirectoryItem` and `endOfDirectory`).
* [x] Ensure `?action=find` successfully returns search results.
* [ ] **Current Task:** Stabilize `?action=getdetails` and `?action=getepisodelist` so Kodi's VideoInfoScanner successfully indexes local `.mkv` files into the database.
* [ ] Wire up the local `anime_mappings.db` to translate IDs (e.g., getting a `tvdb_id` from an `anilist_id`).

### Phase 2: Metadata Providers & Data Enrichment

*Focus: Fetching the actual show data from the internet.*

* [ ] **AniList API (`anilist.py`):** Set up GraphQL queries for primary show info, synopses, and genres.
* [ ] **TVDB/TMDB APIs (`tvdb.py`, `tmdb.py`):** Fetch season/episode structures and exact broadcast dates.
* [ ] **Artwork Engine (`artwork.py`, `fanarttv.xml`):** Aggregate posters, fanart, clear logos, and character art. Prioritize high-resolution links.
* [ ] **Ratings Engine (`ratings.py`):** Implement fallback ratings (e.g., try MAL, fallback to Trakt, fallback to IMDb).

### Phase 3: Edge Cases & Advanced Features

*Focus: Handling weird anime setups and local user overrides.*

* [ ] **NFO Parsing (`nfo.py`):** Allow the scraper to read local `.nfo` files to explicitly set an AniList or TVDB ID, bypassing the search phase.
* [ ] **Formatting Logic (`episodes.py`):** Handle Anime Movies vs. OVAs vs. TV Shows accurately.
* [ ] **Settings Integration (`settings.xml`):** Ensure user preferences (e.g., "Use DVD Order", "Prefer English Dub titles", "Enable Fanart.tv") actively modify the scraping logic.

### Phase 4: Polish, Optimization & Release

*Focus: Making it production-ready for the public.*

* [ ] **Caching (`cache.py`):** Implement local caching for API responses to speed up library updates and prevent rate-limiting/API bans.
* [ ] **Code Cleanup:** Refactor massive files, remove unused imports, and adhere to PEP8/Kodi guidelines.
* [ ] **CI/CD:** Verify the GitHub Action successfully tags, zips, and deploys v1.0.0 to your repository.

---

## 🛠️ Next Steps for Us

To get Phase 1 officially crossed off the list, we need to ensure your local Kodi scanner successfully scrapes that folder of *Steins;Gate* episodes you've been testing.

**Would you like to:**

1. Focus on finishing the `getepisodelist` and `getepisodedetails` logic so the scanner finishes?
2. Look at how we are querying the `anime_mappings.db` to make sure we are passing the right IDs?
3. Review another part of the roadmap?
