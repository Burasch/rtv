#!/bin/bash

# Konfiguration (Diese Variablen werden beim 'docker run' übergeben)
REPO_URL="https://${GITHUB_TOKEN}@github.com/DEIN_NUTZERNAME/DEIN_REPO.git"

# 1. Repository klonen oder aktualisieren
if [ ! -d ".git" ]; then
    echo "Klone Repository..."
    git clone $REPO_URL .
else
    echo "Aktualisiere Repository..."
    git pull origin main
fi

# 2. Playwright Browser installieren (falls nicht im Image-Bau erledigt)
playwright install chromium

# 3. Den Flask-Server im Hintergrund starten
gunicorn --bind 0.0.0.0:8085 app:app &

# 4. Den Scraper/M3U-Generator zum ersten Mal ausführen
python3 scraper.py

# Container am Laufen halten
tail -f /dev/null