import re

file_path = 'scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Wir ersetzen die einfache scrape_stream Funktion durch eine Playwright-Version
new_scrape_logic = r'''
    def scrape_stream(self, url):
        """Nutzt Playwright um dynamische Streams zu finden"""
        logger.info(f"🌐 Öffne Browser für: {url}")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                
                # Wir fangen Netzwerk-Anfragen ab, um .m3u8 zu finden
                found_m3u8 = []
                page.on("request", lambda request: found_m3u8.append(request.url) if ".m3u8" in request.url else None)
                
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(5000) # Warte kurz auf Player-Laden
                
                browser.close()
                
                for link in found_m3u8:
                    if "index" in link or "playlist" in link:
                        if self.validate(link):
                            logger.info(f"✨ Stream gefunden: {link}")
                            return link
        except Exception as e:
            logger.error(f"❌ Playwright Fehler bei {url}: {e}")
        return None
'''

# Ersetzung im Code
content = re.sub(r'    def scrape_stream\(self, url\):.*?return None', new_scrape_logic, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Scraper auf Playwright-Browser umgestellt!")
