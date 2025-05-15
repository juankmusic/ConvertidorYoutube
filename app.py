from flask import Flask, render_template, request, send_file, flash
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ruta a ffmpeg
ffmpeg_path = '/usr/bin/ffmpeg'

# Carpeta de descargas
download_folder = 'downloads'
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    option = request.form['option']
    resolution = request.form.get('resolution', '1080p')  # 1080p, 2k, 4k

    try:
        if option == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            }
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        else:
            height_map = {
                '1080p': '1080',
                '2k': '1440',
                '4k': '2160',
            }
            max_height = height_map.get(resolution, '1080')

            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height<={max_height}]+bestaudio[ext=m4a]/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
            }
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"Hubo un problema al descargar o enviar el archivo: {str(e)}", 'error')
        return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
