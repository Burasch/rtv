import os, json, subprocess, logging
from config import Config
from logo_service import LogoModule

logger = logging.getLogger("DataMgr")

class DataModule:
    @staticmethod
    def update_from_github():
        try:
            subprocess.run(["git", "config", "--global", "--add", "safe.directory", "/app"], check=False)

            if os.path.exists(".git"):
                logger.info("🔄 Synchronisiere mit GitHub...")
                
                # JSON sichern
                json_backup = None
                if os.path.exists("streams-ru.json"):
                    with open("streams-ru.json", "r", encoding='utf-8') as f:
                        json_backup = f.read()

                # Hard Reset - alles sauber von GitHub
                subprocess.run(["git", "fetch", "--all"], check=False)
                subprocess.run(["git", "reset", "--hard", "origin/main"], check=False)

                # JSON wiederherstellen
                if json_backup:
                    with open("streams-ru.json", "w", encoding='utf-8') as f:
                        f.write(json_backup)
                    logger.info("✅ Update sauber. JSON wiederhergestellt.")
                else:
                    logger.info("✅ Update sauber.")
                    
        except Exception as e:
            logger.error(f"Git Fehler: {e}")

    @staticmethod
    def load_json():
        if os.path.exists("streams-ru.json"):
            try:
                with open("streams-ru.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ JSON Lesefehler: {e}. Datei evtl. korrupt.")
        return {}

    @staticmethod
    def save_json(data):
        with open("streams-ru.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def generate_m3u(channels):
        ip = Config.MY_IP
        port = Config.PORT
        epg_url = f"http://{ip}:{port}/{Config.EPG_FILE}"
        with open("/app/RussiTV.m3u8", "w", encoding='utf-8') as f:
            f.write(f'#EXTM3U x-tvg-url="{epg_url}"\n')
            for name, data in channels.items():
                url_name = name.strip().replace(" ", "-")
                proxy_link = f"http://{ip}:{port}/proxy/{url_name}"
                logo_url = LogoModule.get_logo_url(data)
                shift = data.get('tvg_shift', 0)
                shift_str = f' tvg-shift="{shift}"' if shift != 0 else ""
                f.write(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="{logo_url}" group-title="Russia"{shift_str},{name}\n{proxy_link}\n')
        logger.info(f"💾 M3U erstellt")
