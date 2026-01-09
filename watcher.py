import requests
import time
import subprocess
import os

# Die Liste der Sender-IDs, die wir überwachen wollen
CHANNELS = ["rossiya-1", "pervyj-kanal", "ntv", "rossiya-24", "sts"] 
# (Du kannst die Liste beliebig erweitern)

GITHUB_M3U_URL = "https://raw.githubusercontent.com/Burasch/rtv/main/RussiTV.m3u8"
CHECK_INTERVAL = 600  # Alle 10 Minuten prüfen

def get_current_url(channel_id):
    """Holt die aktuelle URL eines Senders von GitHub"""
    try:
        resp = requests.get(GITHUB_M3U_URL, timeout=10)
        if resp.status_code == 200:
            lines = resp.text.splitlines()
            for i, line in enumerate(lines):
                if f'tvg-id="{channel_id}"' in line:
                    return lines[i+1].strip()
    except:
        return None
    return None

def is_url_working(url):
    """Prüft, ob der Stream erreichbar ist"""
    if not url or "offline" in url:
        return False
    try:
        # Wir prüfen nur die ersten Bytes (Timeout 5s)
        with requests.get(url, stream=True, timeout=5) as r:
            if r.status_code == 200:
                return True
    except:
        return False
    return False

def trigger_scraper(channel_id):
    """Startet den Scraper im Docker-Container für eine bestimmte ID"""
    print(f"🚀 Starte Scraper für: {channel_id}")
    # Wir rufen den Scraper innerhalb des laufenden Docker-Containers auf
    subprocess.run(["docker", "exec", "iptv-hub", "python3", "scraper.py", "--limit", channel_id])

print("👀 Wächter gestartet. Überwachung läuft...")

while True:
    for cid in CHANNELS:
        url = get_current_url(cid)
        print(f"🔍 Prüfe {cid}...")
        
        if not is_url_working(url):
            print(f"❌ {cid} ist offline!")
            trigger_scraper(cid)
        else:
            print(f"✅ {cid} ist online.")
            
    print(f"😴 Prüfung beendet. Warte {CHECK_INTERVAL} Sekunden...")
    time.sleep(CHECK_INTERVAL)
