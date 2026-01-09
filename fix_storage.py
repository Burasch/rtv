import re

file_path = 'scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Wir sorgen dafür, dass die Ergebnisse IMMER auch lokal als results.json gespeichert werden
local_save_logic = r'''
    def upload(self):
        # 1. Lokal speichern für die app.py
        try:
            with open('results.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=4)
            logger.info("✅ Ergebnisse lokal in results.json gespeichert!")
        except Exception as e:
            logger.error(f"❌ Fehler beim lokalen Speichern: {e}")

        # 2. Bestehender GitHub Upload
'''

# Ersetzung der upload Funktion
content = re.sub(r'    def upload\(self\):', local_save_logic, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Scraper speichert jetzt lokal für den Proxy!")
