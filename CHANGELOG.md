## [0.9.1] - 2026-06-23

### Fixed
- **Scraper Routing:** Fixed a directory generation error (`GetDirectory - Error`) caused by improper handling of Kodi's `sys.argv[2]` query string. 
- **Parameter Extraction:** Updated `scraper.py` and `actions.py` to utilize `urllib.parse.parse_qs` to safely parse and extract parameters (such as `action` and `title`) instead of relying on hardcoded argument indices and exact string matches.
