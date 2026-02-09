import xml.etree.ElementTree as ET
import gzip
import os

def filter_epg(input_file, output_file, allowed_ids):
    # Öffne die große GZ-Datei
    with gzip.open(input_file, 'rb') as f:
        tree = ET.parse(f)
        root = tree.getroot()

    # Neues Root-Element erstellen
    new_root = ET.Element("tv")
    
    # Nur Channels kopieren, die wir wirklich haben
    for channel in root.findall('channel'):
        if channel.get('id') in allowed_ids:
            new_root.append(channel)

    # Nur Programme kopieren, die zu unseren Channels gehören
    for programme in root.findall('programme'):
        if programme.get('channel') in allowed_ids:
            new_root.append(programme)

    # Als kleine GZ-Datei speichern
    with gzip.open(output_file, 'wb') as f:
        tree = ET.ElementTree(new_root)
        tree.write(f, encoding='utf-8', xml_declaration=True)
