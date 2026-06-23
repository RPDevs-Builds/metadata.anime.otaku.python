import re
import urllib.request
from ..utils import logger

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

def get_filler_data(anime_eng_title):
    filler_list = []
    if anime_eng_title:
        # Generate slug
        anime_url = re.sub(r'\W', '-', anime_eng_title.lower())
        anime_url = re.sub(r'-+', '-', anime_url).strip('-')
        
        url = f"https://www.animefillerlist.com/shows/{anime_url}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
                if HAS_BS4:
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('table', class_="EpisodeList")
                    if table and table.tbody:
                        for tr in table.tbody.find_all('tr'):
                            span = tr.find('span', class_='Type')
                            if span:
                                filler_list.append(span.text.strip())
                else:
                    # Regex fallback: find all rows inside <tbody>
                    tbody_match = re.search(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
                    if tbody_match:
                        tbody_html = tbody_match.group(1)
                        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_html, re.DOTALL)
                        for row in rows:
                            span_match = re.search(r'class=["\']Type["\'][^>]*>(.*?)</span>', row, re.DOTALL)
                            if span_match:
                                text = re.sub(r'<[^>]*>', '', span_match.group(1)).strip()
                                filler_list.append(text)
        except Exception as e:
            logger(f"AnimeFillerList Error: {e}", level="ERROR")
            
    return filler_list
