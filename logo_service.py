import re
import logging
import unicodedata
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

CYRILLIC_TO_LATIN = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo',
    'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
    'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
    'ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch',
    'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    'А':'a','Б':'b','В':'v','Г':'g','Д':'d','Е':'e','Ё':'yo',
    'Ж':'zh','З':'z','И':'i','Й':'y','К':'k','Л':'l','М':'m',
    'Н':'n','О':'o','П':'p','Р':'r','С':'s','Т':'t','У':'u',
    'Ф':'f','Х':'kh','Ц':'ts','Ч':'ch','Ш':'sh','Щ':'shch',
    'Ъ':'','Ы':'y','Ь':'','Э':'e','Ю':'yu','Я':'ya',
}

def _transliterate(text):
    return ''.join(CYRILLIC_TO_LATIN.get(c, c) for c in text)

def _normalize(name):
    t = _transliterate(name)
    t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii')
    t = t.lower()
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return t.strip('-')

def _variants(base):
    if not base:
        return []
    v = [base]
    for sfx in ['-tv','-hd','-sd','-ru','-4k','-plus']:
        if base.endswith(sfx):
            short = base[:-len(sfx)]
            if short and short not in v:
                v.append(short)
    for add in ['-ru','-tv']:
        c = base + add
        if c not in v:
            v.append(c)
    return v

def _lyngsat_urls(candidate):
    first = candidate[0] if candidate else 'a'
    prefix = first + first
    return [
        f"https://www.lyngsat.com/logo/tv/{prefix}/{candidate}.png",
    ]

def _make_session():
    s = requests.Session()
    retry = Retry(total=2, backoff_factor=0.3, status_forcelist=[500,502,503,504])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s

_session = _make_session()

def _url_ok(session, url):
    try:
        r = session.head(url, timeout=4, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False

class LogoModule:
    @staticmethod
    def get_logo_url(channel_data):
        try:
            name = ''
            channel_id = ''

            if isinstance(channel_data, tuple) and len(channel_data) == 2:
                name = str(channel_data[0])
                data = channel_data[1] if isinstance(channel_data[1], dict) else {}
                channel_id = data.get('id', data.get('epg_id', ''))
            elif isinstance(channel_data, dict):
                name = channel_data.get('name', '')
                channel_id = channel_data.get('id', channel_data.get('epg_id', ''))
            elif isinstance(channel_data, str):
                name = channel_data

            candidates = []
            for src in [name, channel_id]:
                if src:
                    for v in _variants(_normalize(src)):
                        if v and v not in candidates:
                            candidates.append(v)

            if not candidates:
                logger.warning(f"LogoModule: Kein Name/ID fuer: {channel_data}")
                return ""

            for cid in candidates:
                url = f"https://toplogos.ru/images/thumbs/preview-logo-{cid}.png"
                if _url_ok(_session, url):
                    logger.info(f"Logo (toplogos): {url}")
                    return url
                for lurl in _lyngsat_urls(cid):
                    if _url_ok(_session, lurl):
                        logger.info(f"Logo (lyngsat): {lurl}")
                        return lurl

            logger.info(f"Kein Logo fuer '{name}'")
            return ""

        except Exception as e:
            logger.error(f"LogoModule Fehler: {e}", exc_info=True)
            return ""
