import requests
import gzip
import xml.etree.ElementTree as ET
import os
import logging
from config import Config
from data_manager import DataModule

logger = logging.getLogger("EPG")

class EPGModule:
    @staticmethod
    def update_epg():
        logger.info("📅 Starte EPG-Download & Filterung...")
        temp_file = "raw_epg.xml.gz"
        output_file = Config.EPG_FILE

        try:
            # 1. Download
            r = requests.get(Config.EPG_SOURCE_URL, stream=True, timeout=30)
            with open(temp_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 2. Sender-IDs laden
            channels = DataModule.load_json()
            allowed_ids = set(channels.keys())
            
            # 3. XML filtern
            with gzip.open(temp_file, 'rb') as f:
                tree = ET.parse(f)
                root = tree.getroot()

            new_root = ET.Element("tv")
            
            # Kanäle filtern
            for channel in root.findall('channel'):
                if channel.get('id') in allowed_ids:
                    new_root.append(channel)
            
            # Programme filtern
            for programme in root.findall('programme'):
                if programme.get('channel') in allowed_ids:
                    new_root.append(programme)

            # 4. Speichern
            with gzip.open(output_file, 'wb') as f:
                new_tree = ET.ElementTree(new_root)
                new_tree.write(f, encoding='utf-8', xml_declaration=True)

            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            logger.info(f"✅ EPG erfolgreich gefiltert gespeichert.")
            return True

        except Exception as e:
            logger.error(f"❌ EPG Fehler: {e}")
            return False
EOF
