from flask import Flask, render_template, request, send_file, flash
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ffmpeg_path = '/usr/bin/ffmpeg'
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
    resolution = request.form.get('resolution', '1080')  # Default to 1080p
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
        else:
            height = int(resolution)
            # Descarga solo si existe exactamente la resolución solicitada
            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height={height}]+bestaudio[ext=m4a]/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
            }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if option == 'audio':
                filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            else:
                filename = ydl.prepare_filename(info_dict)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"No se pudo descargar el video con la resolución {resolution}p. Intenta con otra resolución o revisa el enlace. Detalle: {str(e)}", 'error')
        return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
