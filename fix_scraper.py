import re

file_path = 'scraper.py'
with open(file_path, 'r') as f:
    content = f.read()

# Wir reparieren den Header-String, der den Syntaxfehler verursacht
wrong_line = r"header = '#EXTM3U m3uautoload=1 deinterlace=1 url-tvg=\"http://epg.it999.ru/ru2.xml.gz\" catchup-days=3 cache=1500"
correct_line = "header = '#EXTM3U m3uautoload=1 deinterlace=1 url-tvg=\"http://epg.it999.ru/ru2.xml.gz\" catchup-days=3 cache=1500\\n\\n'"

content = content.replace(wrong_line, correct_line)

# Falls Backslashes in den f-Strings fehlen (wegen der Terminal-Übertragung)
content = content.replace('{res["status_suffix"]}\\n{res["stream"]}', '{res["status_suffix"]}\\n{res["stream"]}')

with open(file_path, 'w') as f:
    f.write(content)
print("✅ Syntaxfehler in scraper.py behoben!")
