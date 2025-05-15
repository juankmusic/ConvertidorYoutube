from flask import Flask, render_template, request, send_file, flash
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ruta a ffmpeg
ffmpeg_path = '/usr/bin/ffmpeg'  # Cambia a tu ruta si estás en Windows

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
            # Descargar siempre el mejor video + mejor audio en MP4
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
            }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

            # Si se convierte a audio, cambiar extensión final
            if option == 'audio':
                filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"Hubo un problema al descargar o enviar el archivo: {str(e)}", 'error')
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
