import re

file_path = 'scraper.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Die verbesserte run-Methode vorbereiten
new_methods = """
    def run(self):
        logger.info(f"🚀 Starte Scraping für {len(self.channels)} Sender...")
        finder = None
        if PLAYWRIGHT_AVAILABLE:
            finder = PlaywrightStreamFinder()
            finder.__enter__()
        try:
            for tvg_id, info in self.channels.items():
                found_url = None
                stable_link = info.get('stable_link')
                if stable_link:
                    logger.info(f"💎 Prüfe stabilen Link für {tvg_id}...")
                    if self.validator.validate_stream(stable_link):
                        logger.info(f"✅ Stabiler Link ist OK!")
                        found_url = stable_link
                if not found_url:
                    sources = info.get('sources', [])
                    for source_url in sources:
                        logger.info(f"🌐 Scrape Quelle für {tvg_id}: {source_url}")
                        streams = finder.find_streams(source_url) if PLAYWRIGHT_AVAILABLE else self.fallback_finder.find_streams(source_url)
                        if streams:
                            for s_url in streams:
                                if self.validator.validate_stream(s_url):
                                    found_url = s_url
                                    break
                        if found_url: break
                status_suffix = ""
                if not found_url:
                    logger.warning(f"❌ Kein Stream für {tvg_id} gefunden!")
                    status_suffix = " (Sender nicht verfügbar)"
                    found_url = "http://0.0.0.0/offline.m3u8"
                self.results.append({
                    "tvg_id": tvg_id,
                    "stream": found_url,
                    "name": info.get('name', tvg_id.replace('-', ' ').upper()),
                    "logo": info.get('logo', ''),
                    "group": info.get('group', 'Russia'),
                    "status_suffix": status_suffix
                })
            self.upload_m3u_to_github()
        finally:
            if finder: finder.__exit__(None, None, None)

    def upload_m3u_to_github(self):
        header = '#EXTM3U m3uautoload=1 deinterlace=1 url-tvg="http://epg.it999.ru/ru2.xml.gz" catchup-days=3 cache=1500\\n\\n'
        lines = [header]
        for res in self.results:
            logo = res['logo'] if res['logo'] else f"https://raw.githubusercontent.com/Burasch/rtv/main/logos/{res['tvg_id']}.png"
            lines.append(f'#EXTINF:-1 tvg-id="{res["tvg_id"]}" tvg-logo="{logo}" group-title="{res["group"]}",{res["name"]}{res["status_suffix"]}\\n{res["stream"]}')
        content = "\\n".join(lines)
        try:
            from github import Github
            g = Github(os.getenv('GITHUB_TOKEN'))
            repo = g.get_repo("Burasch/rtv")
            try:
                f_obj = repo.get_contents("RussiTV.m3u8")
                repo.update_file(f_obj.path, "Auto-Update", content, f_obj.sha)
            except:
                repo.create_file("RussiTV.m3u8", "Initial", content)
            logger.info("✅ GitHub M3U aktualisiert!")
        except Exception as e:
            logger.error(f"❌ GitHub Fehler: {e}")
"""

# 2. Alte run-Methode ersetzen (wir suchen den Start der Methode und löschen bis zum nächsten def)
content = re.sub(r'    def run\(self\):.*?((?=\n    def)|(?=\nif __name__))', new_methods, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
print("✅ scraper.py wurde automatisch erweitert!")
