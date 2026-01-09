import re

file_path = 'scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Die mächtige Scraping-Logik wieder einbauen
advanced_run = r'''
    def run(self):
        logger.info("🚀 Suche nach Live-Streams gestartet...")
        # Wir versuchen Playwright zu laden (für dynamische Seiten)
        try:
            from playwright.sync_api import sync_playwright
            playwright_enabled = True
        except ImportError:
            playwright_enabled = False
            logger.warning("⚠️ Playwright nicht installiert, nutze Basis-Validierung.")

        for tid, info in self.channels.items():
            found_url = None
            
            # 1. Schritt: Prüfe den stabilen Link
            stable = info.get('stable_link')
            if stable and self.validate(stable):
                logger.info(f"✅ Stable Link OK für {tid}")
                found_url = stable
            
            # 2. Schritt: Wenn stable nicht geht, durchsuche die Quellen (Scraping)
            if not found_url and playwright_enabled:
                sources = info.get('sources', [])
                for src in sources:
                    logger.info(f"🔍 Scrape Quelle für {tid}: {src}")
                    # Hier rufen wir die Such-Logik auf
                    found_url = self.scrape_stream(src)
                    if found_url: break

            # Ergebnis speichern
            status = "" if found_url else " (Sender nicht verfügbar)"
            self.results.append({
                "id": tid, 
                "url": found_url if found_url else "http://0.0.0.0/offline.m3u8",
                "status": status,
                "name": info.get('name', tid.upper()),
                "logo": info.get('logo', ''),
                "group": info.get('group', 'Russia')
            })
        self.upload()

    def scrape_stream(self, url):
        """Einfacher Scraper, der nach .m3u8 Links im Seitenquelltext sucht"""
        try:
            r = requests.get(url, timeout=10)
            # Suche nach typischen Stream-Endungen im Quelltext
            matches = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+?\.m3u8', r.text)
            for m in matches:
                if self.validate(m): return m
        except:
            pass
        return None
'''

# Ersetzt die alte run Methode
content = re.sub(r'    def run\(self\):.*?def upload', advanced_run + '\n    def upload', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Scraper-Logik wurde auf 'Suchen' umgestellt!")
