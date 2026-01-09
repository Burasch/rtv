import http.server
import socketserver
import urllib.request
import re

# Wir nutzen Port 8086, um Konflikte mit Docker (8085) zu vermeiden
PORT = 8086 
GITHUB_M3U_URL = "https://raw.githubusercontent.com/Burasch/rtv/main/RussiTV.m3u8"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Die komplette Playlist für Kodi generieren
        if self.path == '/playlist.m3u' or self.path == '/':
            try:
                with urllib.request.urlopen(GITHUB_M3U_URL) as response:
                    content = response.read().decode('utf-8')
                
                host = self.headers.get('Host')
                lines = content.splitlines()
                new_m3u = []
                for line in lines:
                    if line.startswith('http'):
                        # Wir suchen die tvg-id in der Zeile davor
                        last_line = new_m3u[-1] if new_m3u else ""
                        match = re.search(r'tvg-id="([^"]+)"', last_line)
                        if match:
                            cid = match.group(1)
                            new_m3u.append(f"http://{host}/stream/{cid}")
                        else:
                            new_m3u.append(line)
                    else:
                        new_m3u.append(line)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("\n".join(new_m3u).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Fehler beim Laden von GitHub: {e}".encode())

        # 2. Einzelne Stream-Weiterleitung (Redirect)
        elif self.path.startswith('/stream/'):
            channel_id = self.path.split('/')[-1]
            try:
                with urllib.request.urlopen(GITHUB_M3U_URL) as response:
                    content = response.read().decode('utf-8')
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if f'tvg-id="{channel_id}"' in line:
                        target_url = lines[i+1].strip()
                        self.send_response(302)
                        self.send_header('Location', target_url)
                        self.end_headers()
                        return
            except: pass

        self.send_response(404)
        self.end_headers()

print(f"✅ Proxy-Server gestartet auf Port {PORT}")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
    httpd.serve_forever()
