#!/usr/bin/env python3
import os, sys, time, json, re, logging, requests

# Playwright Import
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# KONFIGURATION (Ohne hartcodiertes Token!)
PROXY_HOST = "192.168.178.38:8085"

def check_link_live(url):
    """Prüft schnell, ob ein Link (m3u8) erreichbar ist."""
    if not url: return False
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def scrape_with_playwright(url):
    """Sucht Stream-URL mit Browser-Interaktion."""
    streams = []
    if not PLAYWRIGHT_AVAILABLE: return []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = browser.new_context(user_agent="Mozilla/5.0...")
            page = context.new_page()
            
            # M3U8 Requests abfangen
            page.on("request", lambda req: streams.append(req.url) if ".m3u8" in req.url else None)
            
            # Timeout auf 45s erhöht für langsame Seiten (wie TV3)
            try:
                page.goto(url, timeout=45000, wait_until='load')
                time.sleep(5) # Zeit für Player-Init
                # Klick in die Mitte
                page.mouse.click(400, 300)
                time.sleep(5)
            except: pass
            
            browser.close()
    except Exception as e:
        logger.error(f"Browser-Fehler: {e}")
    return [s for s in list(set(streams)) if "http" in s and ".m3u8" in s]

def main():
    GITHUB_JSON_URL = "https://raw.githubusercontent.com/Burasch/rtv/main/streams-ru.json"
    try:
        channels = requests.get(GITHUB_JSON_URL).json()
    except:
        logger.error("Konnte Liste nicht laden")
        return

    results = {}
    
    for channel_id, data in channels.items():
        logger.info(f"📺 Prüfe: {channel_id}")
        
        # 1. Priorität: Stable Link prüfen
        stable = data.get('stable_link')
        if stable and check_link_live(stable):
            logger.info(f"  ✨ Stable Link funktioniert. Überspringe Scraping.")
            results[channel_id] = {"stream": stable, "proxy": f"http://{PROXY_HOST}/stream/{channel_id}"}
            continue

        # 2. Priorität: Scraping wenn Stable Link fehlt oder tot ist
        logger.info(f"  🔍 Suche neuen Link (Scraping)...")
        found = []
        for source in data.get('sources', []):
            if not source: continue
            found = scrape_with_playwright(source)
            if found: break
        
        if found:
            results[channel_id] = {"stream": found[0], "proxy": f"http://{PROXY_HOST}/stream/{channel_id}"}
            logger.info(f"  ✅ Neuer Link gefunden!")
        else:
            logger.warning(f"  ❌ Kein Link für {channel_id}")

    # Speichern
    with open('streams.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    m3u = "#EXTM3U\n"
    for cid, d in results.items():
        m3u += f'#EXTINF:-1 tvg-id="{cid}", {cid}\n{d["proxy"]}\n'
    
    with open('RussiTV_updated.m3u8', 'w') as f:
        f.write(m3u)
    logger.info("🚀 Alles aktualisiert!")

if __name__ == "__main__":
    main()
