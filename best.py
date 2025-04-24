from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from yt_dlp import YoutubeDL
import os
import re
from threading import Thread

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flashing messages
FFMPEG_PATH = r"D:\\Kuwar Rushikesh\\Kuwar Rushikesh\\ip port checker\\test\\android\\ffmpeg.exe"


DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

progress = {
    'status': '',
    'percentage': 0
}

def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
        downloaded = d.get('downloaded_bytes', 0)
        percentage = int(downloaded * 100 / total_bytes)
        progress['status'] = 'downloading'
        progress['percentage'] = percentage
    elif d['status'] == 'finished':
        progress['status'] = 'finished'
        progress['percentage'] = 100

def download_video_or_audio(url, download_type, quality):
    ydl_opts = {
         'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'ffmpeg_location': FFMPEG_PATH,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'progress_hooks': [progress_hook],
    }

    if download_type == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    elif download_type == 'video' and quality:
        ydl_opts['format'] = f"bestvideo[height<={quality}]+bestaudio/best"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/', methods=['GET', 'POST'])
def index():
    global progress
    progress = {'status': '', 'percentage': 0}
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    global progress
    url = request.form['url']
    download_type = request.form['type']
    quality = request.form.get('quality', '')

    if download_type == 'thumbnail':
        # Redirect to thumbnail route
        return redirect(url_for('download_thumbnail', thumb_url=url))

    try:
        thread = Thread(target=download_video_or_audio, args=(url, download_type, quality))
        thread.start()
        return redirect(url_for('progress_bar'))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('index'))

@app.route('/download_thumbnail')
def download_thumbnail():
    youtube_url = request.args.get("thumb_url")
    match = re.search(r'(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', youtube_url)

    if not match:
        flash("Invalid YouTube URL for thumbnail.", "error")
        return redirect(url_for('index'))

    video_id = match.group(1)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return render_template('index.html', thumbnail_url=thumbnail_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
