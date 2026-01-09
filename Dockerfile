FROM python:3.10-slim

# System-Abhängigkeiten für Playwright und Git
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Browser-Binaries installieren
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Start-Skript ausführbar machen 
RUN chmod +x start.sh

CMD ["./start.sh"]