#!/usr/bin/env python3
import os, json, re, logging, requests, time
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOGO_BASE_URL = "https://raw.githubusercontent.com/Burasch/rtv/main/logos"

def is_link_playable(url):
    if not url or "itv.uz" in url: return False # Bekannte Fake-Links direkt ignorieren
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with requests.get(url, headers=headers, stream=True, timeout=10) as r:
            if r.status_code == 200:
                chunk = next(r.iter_content(512))
                if b"#EXTM3U" in chunk or b"#EXT-X-STREAM" in chunk:
                    return True
    except: pass
    return False

def scrape_with_playwright(url):
    found_streams = []
    try:
        with sync_playwright() as p:
            # Wir nutzen Chromium mit ein paar Extra-Optionen gegen Erkennung
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-blink-features=AutomationControlled'])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()
            
            # Alle Netzwerkanfragen überwachen
            page.on("request", lambda req: found_streams.append(req.url) if ".m3u8" in req.url else None)
            
            logger.info(f"    🌐 Öffne Seite: {url}")
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            # 5 Sekunden warten, dann wild herumklicken/scrollen um Player zu triggern
            time.sleep(5)
            page.mouse.wheel(0, 500)
            time.sleep(2)
            page.mouse.click(640, 360) # Klick in die Mitte des Bildschirms
            
            # Nochmal 10 Sekunden warten, damit der Stream laden kann
            time.sleep(10)
            
            browser.close()
    except Exception as e:
        logger.error(f"    ⚠️ Browser-Fehler: {e}")
    
    # Filtern: Nur echte HTTP-Links, keine Blobs oder Data-URLs
    return [s for s in list(set(found_streams)) if s.startswith("http") and ".m3u8" in s]

def main():
    json_path = "streams-ru.json"
    if not os.path.exists(json_path): return

    with open(json_path, 'r', encoding='utf-8') as f:
        channels = json.load(f)

    updated_channels = channels.copy()
    m3u_lines = ["#EXTM3U\n"]

    for channel_id, data in channels.items():
        logger.info(f"📺 Kanal: {channel_id}")
        final_stream = None
        
        # 1. Bestehenden Link testen
        if data.get('stable_link') and is_link_playable(data['stable_link']):
            logger.info("  ✨ Bestehender Link OK.")
            final_stream = data['stable_link']
        else:
            # 2. Quellen durchsuchen
            sources = data.get('sources', [])
            for i, src in enumerate(sources):
                if not src: continue
                candidates = scrape_with_playwright(src)
                for cand in candidates:
                    if is_link_playable(cand):
                        final_stream = cand
                        if i > 0: # Sortierung verbessern
                            sources.insert(0, sources.pop(i))
                            updated_channels[channel_id]['sources'] = sources
                        break
                if final_stream: break

        if final_stream:
            updated_channels[channel_id]['stable_link'] = final_stream
            logo = f"{LOGO_BASE_URL}/{channel_id}.png"
            name = channel_id.replace("-", " ").upper()
            m3u_lines.append(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" group-title="Russia",{name}\n{final_stream}\n')
            logger.info(f"  ✅ Stream gefunden!")
        else:
            logger.warning(f"  ❌ Kein Stream für {channel_id}")

    with open('RussiTV.m3u8', 'w', encoding='utf-8') as f: f.writelines(m3u_lines)
    with open('streams-ru.json', 'w', encoding='utf-8') as f: json.dump(updated_channels, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
