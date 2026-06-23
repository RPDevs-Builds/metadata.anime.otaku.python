# Changelog

All notable changes to `metadata.anime.otaku.python` will be documented in this file.

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
