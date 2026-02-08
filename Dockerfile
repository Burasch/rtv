FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# System-Abhängigkeiten (git wird für DataModule.update_from_github benötigt)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Python-Bibliotheken
RUN pip install playwright requests

# Browser für den Scraper-Service installieren
RUN playwright install chromium
RUN playwright install-deps chromium

# Projektdateien kopieren
COPY . .

# Startbefehl: -u erzwingt "unbuffered" Logs, damit du sie sofort in 'docker logs' siehst
CMD ["python3", "-u", "main.py"]
