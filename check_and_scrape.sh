#!/bin/bash
cd ~/Docker-Container/IPTV/iptv-hub/

# 1. Prüfen, ob der Container läuft
if [ "$(docker inspect -f '{{.State.Running}}' iptv-hub)" != "true" ]; then
    docker start iptv-hub
fi

# 2. Scraper starten (er prüft die Sender und aktualisiert nur bei Bedarf)
docker exec -it iptv-hub python3 /app/scraper.py

# 3. Wenn Änderungen da sind, hochladen
./finish.sh
