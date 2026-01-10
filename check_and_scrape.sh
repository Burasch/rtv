#!/bin/bash
# In das Verzeichnis wechseln
cd /home/alex/Docker-Container/IPTV/iptv-hub/

# Log-Datei starten
echo "--- Lauf am $(date) ---" >> cron.log

# 1. Scraper im Container ausführen
/usr/bin/docker exec iptv-hub python3 /app/scraper.py >> cron.log 2>&1

# 2. Dateien aus dem Container kopieren
/usr/bin/docker cp iptv-hub:/app/RussiTV.m3u8 . >> cron.log 2>&1
/usr/bin/docker cp iptv-hub:/app/streams-ru.json . >> cron.log 2>&1

# 3. Zu GitHub pushen
/usr/bin/git add RussiTV.m3u8 streams-ru.json >> cron.log 2>&1
/usr/bin/git commit -m "Automatisches Update $(date)" >> cron.log 2>&1
/usr/bin/git push origin main >> cron.log 2>&1

echo "Lauf beendet." >> cron.log
