import re

file_path = 'scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Die neuen, sauberen Methoden
new_logic = r'''
    def run(self):
        logger.info(f"🚀 Starte Scraping...")
        finder = None
        if PLAYWRIGHT_AVAILABLE:
            finder = PlaywrightStreamFinder()
            finder.__enter__()
        try:
            for tvg_id, info in self.channels.items():
                found_url = None
                stable_link = info.get('stable_link')
                if stable_link and self.validator.validate_stream(stable_link):
                    logger.info(f"✅ Stable OK: {tvg_id}")
                    found_url = stable_link
                if not found_url:
                    for src in info.get('sources', []):
                        streams = finder.find_streams(src) if PLAYWRIGHT_AVAILABLE else self.fallback_finder.find_streams(src)
                        if streams:
                            for s in streams:
                                if self.validator.validate_stream(s):
                                    found_url = s; break
                        if found_url: break
                
                status = "" if found_url else " (Sender nicht verfügbar)"
                self.results.append({
                    "tvg_id": tvg_id,
                    "stream": found_url if found_url else "http://0.0.0.0/offline.m3u8",
                    "name": info.get('name', tvg_id.upper()),
                    "logo": info.get('logo', ''),
                    "group": info.get('group', 'Russia'),
                    "status": status
                })
            self.upload_m3u_to_github()
        finally:
            if finder: finder.__exit__(None, None, None)

    def upload_m3u_to_github(self):
        header = "#EXTM3U m3uautoload=1 deinterlace=1 url-tvg=\"http://epg.it999.ru/ru2.xml.gz\" catchup-days=3 cache=1500\n\n"
        lines = [header]
        for r in self.results:
            logo = r['logo'] if r['logo'] else f"https://raw.githubusercontent.com/Burasch/rtv/main/logos/{r['tvg_id']}.png"
            lines.append(f'#EXTINF:-1 tvg-id="{r["tvg_id"]}" tvg-logo="{logo}" group-title="{r["group"]}",{r["name"]}{r["status"]}\n{r["stream"]}')
        content = "\n".join(lines)
        try:
            from github import Github
            g = Github(os.getenv("GITHUB_TOKEN"))
            repo = g.get_repo("Burasch/rtv")
            f_obj = repo.get_contents("RussiTV.m3u8")
            repo.update_file(f_obj.path, "Auto-Update", content, f_obj.sha)
            logger.info("✅ GitHub M3U aktualisiert!")
        except Exception as e:
            logger.error(f"❌ GitHub Fehler: {e}")
'''

# Wir ersetzen alles ab 'def run(self):' bis zum Ende der Klasse oder Datei
content = re.sub(r'    def run\(self\):.*', new_logic, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
