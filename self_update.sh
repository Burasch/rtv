
#!/bin/bash
echo "🔍 Prüfe auf Code-Updates (nur Scripte)..."
cd /app

# Aktuellen Stand von GitHub holen ohne zu mergen
git fetch origin main

# Prüfen ob Updates da sind
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "🆕 Update gefunden! Aktualisiere Code..."
    
    # NUR Python Dateien und Docker-Files holen, streams-ru.json ignorieren
    git checkout origin/main -- *.py Dockerfile docker-compose.yml
     
    # Den neuen Commit-Stand lokal markieren
    git merge origin/main --ff-only
    
    echo "✅ Code aktualisiert. Starte Prozess neu..."
    pkill -f main.py
else
    echo "✅ Code ist auf dem neuesten Stand."
fi
