import socket, os

def get_self_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class Config:
    MY_IP = get_self_ip()
    PORT = 2022
    GITHUB_REPO_URL = "https://github.com/Burasch/rtv.git"
    EPG_SOURCE_URL = "https://iptvx.one/epg/epg.xml.gz"
    EPG_FILE = "epg.xml.gz"
    ERROR_VIDEO = f"http://{MY_IP}:{PORT}/stoerung.mp4"
    CHECK_INTERVAL = 1800 
