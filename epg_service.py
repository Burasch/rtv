# epg_service.py
import requests
import gzip
import xml.etree.ElementTree as ET
import os
import logging
import re
from config import Config
from data_manager import DataModule

logger = logging.getLogger("EPG")


def _normalize(text: str) -> str:
    """Kleinbuchstaben, nur Buchstaben/Ziffern, Leerzeichen weg."""
    return re.sub(r'[^a-zа-яё0-9]', '', text.lower().strip())


class EPGModule:

    @staticmethod
    def _build_id_sets(channels: dict) -> tuple:
        primary_ids = set()
        epg_ids = set()
        epg_to_key = {}

        for key, data in channels.items():
            primary_ids.add(key)
            epg_id = data.get("epg_id", "").strip()
            if epg_id:
                epg_ids.add(epg_id)
                epg_to_key[epg_id] = key

        return primary_ids, epg_ids, epg_to_key

    @staticmethod
    def _build_name_index(channels: dict) -> dict:
        """
        Baut einen Index: normalisierter Kanalname → Original-Key
        Für Fuzzy-Match über EPG-Display-Namen.
        """
        name_to_key = {}
        for key in channels:
            norm = _normalize(key)
            if norm:
                name_to_key[norm] = key
        return name_to_key

    @staticmethod
    def _match_channel_by_name(channel_elem, name_to_key: dict):
        """
        Prüft alle <display-name> eines EPG-Kanals gegen unsere Kanalnamen.
        Gibt den gematchten Key zurück oder None.
        """
        for dn in channel_elem.findall('display-name'):
            text = dn.text or ''
            norm = _normalize(text)
            if norm in name_to_key:
                return name_to_key[norm]
        return None

    @staticmethod
    def update_epg():
        logger.info("📅 Starte EPG-Download & Filterung...")
        temp_file = "raw_epg.xml.gz"
        output_file = Config.EPG_FILE

        try:
            # ── 1. Download ──────────────────────────────────────
            r = requests.get(
                Config.EPG_SOURCE_URL,
                stream=True,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            r.raise_for_status()

            with open(temp_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"📦 Download: {os.path.getsize(temp_file) / 1024 / 1024:.1f} MB")

            # ── 2. Sender-IDs laden ──────────────────────────────
            channels = DataModule.load_json()
            if not channels:
                logger.error("❌ channels.json ist leer!")
                return False

            primary_ids, epg_ids, epg_to_key = EPGModule._build_id_sets(channels)
            name_to_key = EPGModule._build_name_index(channels)

            logger.info(f"📋 {len(primary_ids)} Kanäle, {len(epg_ids)} EPG-IDs")

            # ── 3. XML parsen ────────────────────────────────────
            with gzip.open(temp_file, 'rb') as f:
                tree = ET.parse(f)
                root = tree.getroot()

            new_root = ET.Element("tv")

            # ── 4. Kanäle filtern (3 Stufen) ─────────────────────
            # Mapping: original EPG-XML-ID → unser Key (für Programme-Phase)
            xml_id_to_key = {}
            matched_channels = 0
            matched_via_epg_id = 0
            matched_via_name = 0

            for channel in root.findall('channel'):
                cid = channel.get('id', '')

                if cid in primary_ids:
                    # Stufe 1: Direkter Match über Kanal-Key
                    new_root.append(channel)
                    xml_id_to_key[cid] = cid
                    matched_channels += 1

                elif cid in epg_ids:
                    # Stufe 2: Match über epg_id
                    original_key = epg_to_key[cid]
                    channel.set('id', original_key)
                    new_root.append(channel)
                    xml_id_to_key[cid] = original_key
                    matched_channels += 1
                    matched_via_epg_id += 1

                else:
                    # Stufe 3: Fuzzy-Match über display-name
                    matched_key = EPGModule._match_channel_by_name(channel, name_to_key)
                    if matched_key:
                        channel.set('id', matched_key)
                        new_root.append(channel)
                        xml_id_to_key[cid] = matched_key
                        matched_channels += 1
                        matched_via_name += 1

            # ── 5. Programme filtern ─────────────────────────────
            matched_programmes = 0

            for programme in root.findall('programme'):
                pid = programme.get('channel', '')

                if pid in xml_id_to_key:
                    # Umbenennen auf unseren Key
                    programme.set('channel', xml_id_to_key[pid])
                    new_root.append(programme)
                    matched_programmes += 1

            logger.info(
                f"✅ Gefiltert: {matched_channels} Kanäle "
                f"({matched_via_epg_id} via epg_id, "
                f"{matched_via_name} via Name), "
                f"{matched_programmes} Sendungen"
            )

            # Nicht gematchte Kanäle loggen
            matched_keys = set(xml_id_to_key.values())
            unmatched = primary_ids - matched_keys
            if unmatched:
                logger.warning(f"⚠️ Ohne EPG: {sorted(unmatched)}")

            # ── 6. Speichern ─────────────────────────────────────
            with gzip.open(output_file, 'wb') as f:
                new_tree = ET.ElementTree(new_root)
                new_tree.write(f, encoding='utf-8', xml_declaration=True)

            logger.info(
                f"💾 EPG: {output_file} "
                f"({os.path.getsize(output_file) / 1024:.0f} KB)"
            )
            return True

        except requests.RequestException as e:
            logger.error(f"❌ Download-Fehler: {e}")
            return False
        except ET.ParseError as e:
            logger.error(f"❌ XML-Fehler: {e}")
            return False
        except Exception as e:
            logger.exception(f"❌ EPG-Fehler: {e}")
            return False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
