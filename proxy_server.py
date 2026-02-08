import http.server, socketserver, threading, logging, os
from urllib.parse import unquote
from config import Config
from data_manager import DataModule
from tools import Tools
from scraper_service import ScraperModule

logger = logging.getLogger("Proxy")
scrape_lock = threading.Lock()

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Fall: Stream Anfrage
        if self.path.startswith('/proxy/'):
            raw_name = unquote(self.path[7:]).strip()
            name_with_spaces = raw_name.replace("-", " ")
            
            channels = DataModule.load_json()
            target = Config.ERROR_VIDEO
            channel_data = channels.get(name_with_spaces) or channels.get(raw_name)

            if channel_data:
                # A) Smotrim Live-Check
                p_link = channel_data.get('permanent_link', "")
                if "smotrim.ru" in p_link and "m3u8" not in p_link:
                    logger.info(f"🔄 Smotrim Live-Scrape für {raw_name}...")
                    found = ScraperModule.find_stream(p_link)
                    if found: target = found[0]

                # B) Normaler Check
                elif Tools.is_link_playable(channel_data.get('stable_link')):
                    target = channel_data.get('stable_link')
                
                # C) Reparatur
                else:
                    logger.info(f"🚨 Link tot für {raw_name}. Starte Suche...")
                    sources = []
                    if p_link: sources.append(p_link)
                    sources.extend(channel_data.get('sources', []))
                    
                    with scrape_lock:
                        for src in sources:
                            found = ScraperModule.find_stream(src)
                            if found and Tools.is_link_playable(found[0]):
                                target = found[0]
                                channel_data['stable_link'] = target
                                DataModule.save_json(channels)
                                break

            self.send_response(302)
            self.send_header('Location', target)
            self.end_headers()
        
        # 2. Fall: Alles andere (EPG, Stoerung.mp4, Logos falls lokal)
        else:
            super().do_GET()

def start_server():
    os.chdir("/app") # Wichtig für SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("", Config.PORT), ProxyHandler)
    logger.info(f"🚀 Proxy läuft auf Port {Config.PORT}")
    server.serve_forever()
