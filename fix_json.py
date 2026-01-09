import json
import re

file_path = 'streams-ru.json'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = f.read()
    
    # Entfernt ungültige Steuerzeichen (Control Characters), außer Zeilenumbrüche
    clean_data = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', raw_data)
    
    # Validierungstest
    json_obj = json.loads(clean_data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)
    print("✅ streams-ru.json wurde erfolgreich repariert und formatiert!")
except Exception as e:
    print(f"❌ Fehler bei der Reparatur: {e}")
