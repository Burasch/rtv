#!/bin/bash
# 1. Änderungen von GitHub holen
git pull origin main

# 2. Den Scraper im Container ausführen
docker exec -it iptv-hub python3 scraper.py

# 3. Die erzeugte Liste aus dem Container auf den Server kopieren
docker cp iptv-hub:/app/RussiTV_updated.m3u8 .
docker cp iptv-hub:/app/streams.json .

# 4. Alles zu GitHub hochladen
git add .
git commit -m "Automatisches Update: $(date +%H:%M)"
git push origin main

echo "✅ RussiTV_updated wurde aktualisiert und hochgeladen."
