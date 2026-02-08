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
                p_link = channel_data.get('permanent_link', "")
                # Smotrim Logik...
                if "smotrim.ru" in p_link and "m3u8" not in p_link:
                    found = ScraperModule.find_stream(p_link)
                    if found: target = found[0]
                elif Tools.is_link_playable(channel_data.get('stable_link')):
                    target = channel_data.get('stable_link')
                else:
                    # Reparatur Logik...
                    sources = [p_link] if p_link else []
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
        
        # 2. Fall: M3U oder EPG direkt ausliefern
        elif self.path.endswith('.m3u8') or self.path.endswith('.xml.gz'):
            file_path = os.path.join("/app", self.path.lstrip('/'))
            if os.path.exists(file_path):
                self.send_response(200)
                # Richtige Header für IPTV Player
                if self.path.endswith('.m3u8'):
                    self.send_header('Content-type', 'application/x-mpegurl')
                else:
                    self.send_header('Content-type', 'application/x-gzip')
                
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Datei nicht gefunden")
        
        # 3. Fall: Alles andere (Logos, mp4)
        else:
            super().do_GET()

def start_server():
    # Wir erzwingen das Verzeichnis /app
    os.chdir("/app")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", Config.PORT), ProxyHandler) as httpd:
        logger.info(f"🚀 Proxy & File-Server läuft auf Port {Config.PORT}")
        httpd.serve_forever()
