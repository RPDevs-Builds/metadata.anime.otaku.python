# Changelog

All notable changes to `metadata.anime.otaku.python` will be documented in this file.

## [1.2.0] - 2026-06-23

### Added
- **Advanced Renamer Options**: Added comprehensive folder, season, and episode formatting options for the Otaku Renamer tool. You can now define whether to add years to base directories, toggle `Season 01` sub-folders, and strip titles down to minimal `S01E01` formats.

## [1.1.2] - 2026-06-23

### Added
- **Fanart.tv Premium Artwork Provider:** Added a dedicated Fanart.tv API scraper to fetch high-quality UI assets including `clearlogo`, `clearart`, `thumb`, and alternate backgrounds.
- **Granular Artwork Toggles:** Expanded the Fan Art settings tab with toggles to selectively enable/disable clearlogos and clearart, alongside a new input field for personal Fanart.tv API keys.
- **Transparent Logo Injection:** Updated the UI injector logic inside both TV Shows (`actions.py`) and Anime Movies (`movies.py`) to properly inject transparent clearlogos using `.setArt()` and `.addAvailableArtwork()` so modern Kodi skins can correctly display them.

---

## [1.1.1] - 2026-06-23

### Added
- **Tabbed Settings Configuration (`settings.xml`):** Completely refactored the settings dialog into semantic categories: Indexer, Renamer, Metadata, Fan Art, Accounts, Logging, and Advanced.
- **Granular Multi-Source Ratings Engine (`actions.py`):** Added support for selecting primary rating sources (AniList, MyAnimeList, TMDb, Simkl) with a fallback lookup chain. Integrated multi-rating injection using Kodi 20's `VideoInfoTag.setRating()` interface.
- **Enhanced Plot & Air Date Selection:** Toggles to configure preferred providers (`plot_source` and `release_date_source`) between AniList, TMDb, and TVDB.
- **Extended Fan Art & Metadata Controls:** Added user toggles for posters, banners, fanart, trailers, and cast.
- **Otaku Renamer Enhancements (`otaku_renamer.py`):** Added recursive subdirectory scanning, parent folder context resolution for nested season folders, absolute-to-season continuation mapping for split seasons, and prefix-collision stripping.

### Fixed
- **English Title Default Fallback:** Fixed a bug where case-insensitive lookup check failed to match `"English"` (default addon setting) with `'english'` inside the code, causing Romaji titles to display by default.

---

## [1.1.0] - 2026-06-23

### Added
- **Batch Context Menu Processing:** Context menu renamer now robustly detects and processes both single show directories and entire parent library directories containing multiple shows.
- **Kodi Progress Bar Feedback:** Shows active folder scanning and mapping progress in the Kodi UI dialog.

## [1.0.9] - 2026-06-23

### Fixed
- Addressed strict Kodi ZIP archive validation bug (`itemsize: 11, first item is folder: false`) by compiling with Python `zipfile`.

---
## [1.0.8] - 2026-06-23

### Added
- **Kodi Context Menu Integration (`kodi.context.item`):** Added right-click support to rename Anime directories directly from the Kodi UI.

### Fixed
- **Renamer Safety:** Rewrote `otaku_renamer.py` regex safety protocols to prevent accidental file overwrites during batch operations.

---

## [1.0.7] - 2026-06-23

### Added
- **NFO Parsing (`nfo.py`):** Added support for parsing local `tvshow.nfo` files to automatically map explicitly specified AniList or MyAnimeList ID tags, allowing users to bypass the search index and force exact matches.

### Fixed
- **Episode Scanning (0 Episodes Added Bug):** Restored the backwards-compatible `liz.setInfo('video', details)` metadata payload to `get_episode_details`. This fixes a critical edge-case bug where the Kodi 19/20 `VideoInfoScanner` silently dropped successfully fetched episodes because the modern `VideoInfoTag` component lacked sufficient legacy metadata binding.

---

## [1.0.6] - 2026-06-23

### Added
- **Multi-Provider Episode Metadata Engine (`metadata_engine.py`):** Parallel async fetching via `concurrent.futures.ThreadPoolExecutor` from AniZip, Jikan, Kitsu, Simkl, and TVDB.
- **AniList Provider (`anilist.py`):** Full GraphQL queries for show search, high-level series details, cover art, banner, studio, genres, and premiered date.
- **TMDb Provider (`tmdb.py`):** Real API integration for TV series details, season/episode iteration, and per-episode still images.
- **Local SQLite Cache (`database.py`, `database_sync.py`):** TTL-based `cache.db` with WAL mode, auto-initialized at scraper startup.
- **DB Connector (`db_connector.py`):** Read-only query interface for the bundled `anime_mappings.db` (6MB community cross-ID mapping table).
- **Filler Tag Support (`anime_filler.py`):** Optional `[Filler]` title prefixes sourced from AnimeFillerList.com, controlled by user setting.
- **Dual InfoTagVideo Mode:** All episode/series list items use both legacy `setInfo('video', ...)` and modern `liz.getVideoInfoTag()` (Kodi 20+ Nexus/Omega) with graceful fallback.
- **Settings UI (`settings.xml`):** Provider toggles (AniZip, Jikan, Kitsu, Simkl, TVDB), API key fields, filler tag toggle, and auto-update interval.
- **CI/CD Pipeline (`.github/workflows/release.yml`):** Automated build, zip packaging, and GitHub Release creation on both `main` branch pushes (pre-release "dev") and `v*` tag pushes (stable release).

### Fixed
- **CI/CD — Tag Trigger:** `on.push.tags` was empty; version tag pushes (e.g. `git tag v1.0.6 && git push --tags`) now correctly trigger the release pipeline.
- **CI/CD — Pre-release Logic:** Tagged releases are now correctly marked as stable; only `main`-branch dev builds are flagged as `prerelease: true`.
- **CI/CD — Tag Push Guard:** `Commit and Push to Repo` step now has an `if: !startsWith(github.ref, 'refs/tags/')` guard, preventing a broken `git push origin HEAD:v1.0.6` on tag triggers.

---

## [0.9.1] - 2026-06-23

### Fixed
- **Scraper Routing:** Fixed a directory generation error (`GetDirectory - Error`) caused by improper handling of Kodi's `sys.argv[2]` query string.
- **Parameter Extraction:** Updated `scraper.py` and `actions.py` to utilize `urllib.parse.parse_qs` to safely parse and extract parameters (such as `action` and `title`) instead of relying on hardcoded argument indices and exact string matches.
