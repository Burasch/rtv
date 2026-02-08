import time, logging
from playwright.sync_api import sync_playwright
from tools import Tools

logger = logging.getLogger("Scraper")

class ScraperModule:
    @staticmethod
    def find_stream(url):
        if not url: return []
        found = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page()
                page.on("request", lambda r: found.append(r.url) if ".m3u8" in r.url.lower() and ".ts" not in r.url.lower() else None)
                page.goto(url, timeout=30000, wait_until="networkidle")
                time.sleep(6)
                browser.close()
        except Exception as e:
            logger.error(f"Scrape Fehler: {e}")
        return [Tools.clean_url(s) for s in found if ".m3u8" in s]
