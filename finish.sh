#!/bin/bash
# 1. Update vom Repository
git pull origin main

# 2. Datei in den korrekten Pfad im Container schieben
docker exec -it iptv-hub mkdir -p /app
docker cp scraper.py iptv-hub:/app/scraper.py

# 3. Scraper ausführen und warten
echo "🚀 Scraper läuft..."
docker exec -it iptv-hub python3 /app/scraper.py

# 4. Ergebnisse zurückkopieren
if docker cp iptv-hub:/app/RussiTV_updated.m3u8 . ; then
    docker cp iptv-hub:/app/streams.json .
    echo "✅ Dateien erfolgreich extrahiert."
    
    # 5. Git Update
    git add .
    git commit -m "Automatisches Update: $(date +%H:%M) - Kodi Fix aktiv"
    git push origin main
    echo "✅ Update auf GitHub veröffentlicht."
else
    echo "❌ Fehler: Datei RussiTV_updated.m3u8 wurde nicht erstellt!"
fi
