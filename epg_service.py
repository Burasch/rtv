import os, requests, logging
from config import Config

logger = logging.getLogger("EPG")

class EPGModule:
    @staticmethod
    def update_epg():
        """Lädt die EPG-Datei herunter, wenn sie fehlt oder alt ist."""
        try:
            logger.info("📅 Prüfe EPG Update...")
            r = requests.get(Config.EPG_SOURCE_URL, stream=True, timeout=20)
            if r.status_code == 200:
                with open(Config.EPG_FILE, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                logger.info("✅ EPG erfolgreich aktualisiert.")
            else:
                logger.warning("⚠️ EPG Download fehlgeschlagen.")
        except Exception as e:
            logger.error(f"EPG Fehler: {e}")
