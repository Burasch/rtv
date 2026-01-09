from flask import Flask, redirect, jsonify, request, Response
import json
import os

app = Flask(__name__)

def get_latest_results():
    try:
        if os.path.exists('results.json'):
            with open('results.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

@app.route('/stream/<channel_id>')
def proxy_stream(channel_id):
    results = get_latest_results()
    for res in results:
        if res['id'] == channel_id:
            url = res.get('url')
            if url and "offline" not in url and "0.0.0.0" not in url:
                return redirect(url)
    return jsonify({"error": "Stream nicht verfügbar"}), 404

@app.route('/playlist.m3u')
def generate_m3u():
    # Erkennt automatisch die IP des Pi (egal ob 192.168.1.5 oder 178.38)
    host = request.host
    results = get_latest_results()
    
    m3u = "#EXTM3U\n"
    for res in results:
        name = res.get('name', res['id'].upper())
        logo = res.get('logo', '')
        group = res.get('group', 'Russia')
        m3u += f'#EXTINF:-1 tvg-id="{res["id"]}" tvg-logo="{logo}" group-title="{group}",{name}\n'
        m3u += f'http://{host}/stream/{res["id"]}\n'
    
    return Response(m3u, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085)
