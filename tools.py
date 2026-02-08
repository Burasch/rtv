import re, requests
from urllib.parse import unquote

class Tools:
    @staticmethod
    def clean_url(url):
        if not url: return url
        url = unquote(url)
        if "file=" in url: url = url.split("file=")[-1]
        match = re.search(r'(https?://[^\s&"\'<>]+?\.m3u8[^\s&"\'<>]*)', url)
        return match.group(1) if match else url

    @staticmethod
    def is_link_playable(url):
        if not url or "stoerung.mp4" in url: return False
        if "smotrim.ru" in url and "m3u8" not in url: return False
        try:
            r = requests.get(url, timeout=5, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            return r.status_code == 200
        except: return False
