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
                browser = p.chromium.launch(
                    headless=True, 
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                # Unnötige Ressourcen blockieren (spart Bandbreite & verhindert Timeouts)
                page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf}", lambda route: route.abort())

                # M3U8 Links beim Netzwerk-Monitoring abfangen
                page.on("request", lambda r: found.append(r.url) if ".m3u8" in r.url.lower() and ".ts" not in r.url.lower() else None)

                try:
                    # domcontentloaded statt networkidle nutzen
                    page.goto(url, timeout=15000, wait_until="domcontentloaded")
                    time.sleep(4)  # Kurz warten, bis der Player das M3U8-Skript ausführt
                except Exception as goto_err:
                    logger.warning(f"Goto-Hinweis für {url}: {goto_err}")

                browser.close()
        except Exception as e:
            logger.error(f"Scrape Fehler: {e}")
            
        return list(dict.fromkeys(Tools.clean_url(s) for s in found if ".m3u8" in s))
        
