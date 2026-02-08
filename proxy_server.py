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
        # 1. Fall: Playlist (.m3u8) oder EPG (.xml.gz) ausliefern
        if self.path.endswith('.m3u8') or self.path.endswith('.xml.gz'):
            file_path = os.path.join("/app", self.path.lstrip('/'))
            if os.path.exists(file_path):
                self.send_response(200)
                
                # Wichtig für Kodi & Co: UTF-8 und richtiger Content-Type
                if self.path.endswith('.m3u8'):
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                else:
                    self.send_header('Content-type', 'application/x-gzip')
                
                # Datei einlesen und senden
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "Datei nicht gefunden")
                return

        # 2. Fall: Stream Proxy (Redirect zu den eigentlichen Stream-Links)
        if self.path.startswith('/proxy/'):
            # URL-Encoding fixen (wichtig für russische Sendernamen)
            raw_name = unquote(self.path[7:]).strip()
            name_with_spaces = raw_name.replace("-", " ")
            
            channels = DataModule.load_json()
            target = Config.ERROR_VIDEO
            
            # Kanal in der Datenbank suchen
            channel_data = channels.get(name_with_spaces) or channels.get(raw_name)

            if channel_data:
                # Prüfen, ob der aktuelle Link noch läuft, sonst Scraper nutzen
                if Tools.is_link_playable(channel_data.get('stable_link')):
                    target = channel_data.get('stable_link')
                else:
                    logger.info(f"🚨 Link für {raw_name} tot. Suche Ersatz...")
                    p_link = channel_data.get('permanent_link', "")
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

            # Redirect zum finalen Stream-Link
            self.send_response(302)
            self.send_header('Location', target)
            self.end_headers()
            return
        
        # 3. Fall: Standard (z.B. für lokale Logos oder Fehler-Videos)
        super().do_GET()

def start_server():
    # Sicherstellen, dass wir im App-Verzeichnis sind
    if os.path.exists("/app"):
        os.chdir("/app")
    
    # Port sofort wieder freigeben bei Neustart
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", Config.PORT), ProxyHandler) as httpd:
        logger.info(f"🚀 Proxy & File-Server läuft auf Port {Config.PORT}")
        httpd.serve_forever()
