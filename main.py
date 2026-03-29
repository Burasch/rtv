#!/usr/bin/env python3
import time, threading, logging, sys
from config import Config
from data_manager import DataModule
from epg_service import EPGModule
from proxy_server import start_server
from tools import Tools
from scraper_service import ScraperModule

# Ressourcen-Fix: Level auf WARNING gesetzt. Reduziert Logs auf ein Minimum!
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")

def background_maintenance():
    while True:
        # 1. GitHub Update separat abfangen
        try:
            DataModule.update_from_github()
        except Exception as e:
            logger.error(f"⚠️ GitHub-Update fehlgeschlagen, wird übersprungen: {e}")

        # 2. EPG separat abfangen, damit bei Ausfall das Programm weiterläuft!
        try:
            EPGModule.update_epg()
        except Exception as e:
            logger.error(f"⚠️ EPG-Update fehlgeschlagen, wird übersprungen: {e}")
        
        # 3. Eigentliche Sender-Prüfung
        try:
            channels = DataModule.load_json()
            changed = False
            
            for name, data in channels.items():
                stable_link = data.get('stable_link')
                if not Tools.is_link_playable(stable_link):
                    # Bei WARNING loggen wir trotzdem Infos zu reparierten Sendern über logger.warning
                    logger.warning(f"🚨 Sender '{name}' offline. Suche Ersatz...")
                    
                    sources = []
                    if data.get('permanent_link'): sources.append(data.get('permanent_link'))
                    sources.extend(data.get('sources', []))
                    
                    for src in sources:
                        found = ScraperModule.find_stream(src)
                        if found and Tools.is_link_playable(found[0]):
                            data['stable_link'] = found[0]
                            changed = True
                            logger.warning(f"✅ Sender '{name}' im Hintergrund repariert.")
                            break
            
            if changed:
                DataModule.save_json(channels)
                DataModule.generate_m3u(channels)
            
            time.sleep(Config.CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Fehler bei der Sender-Wartung: {e}")
            time.sleep(60)

def main():
    channels = DataModule.load_json()
    DataModule.generate_m3u(channels)
    
    threading.Thread(target=start_server, daemon=True).start()
    maintenance_thread = threading.Thread(target=background_maintenance, daemon=True)
    maintenance_thread.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: sys.exit(0)

if __name__ == "__main__":
    main()
