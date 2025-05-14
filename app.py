from flask import Flask, render_template, request, send_file, flash
from yt_dlp import YoutubeDL
import os
import subprocess

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
    video_format = request.form['format']  # mp3 / mp4 / mp4_hd / webm

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
        # Configuraciones comunes para formatos de video
        if video_format in ['mp4', 'mp4_hd']:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
            }
        elif video_format == 'webm':
            ydl_opts = {
                'format': 'bestvideo[ext=webm][height<=1080]+bestaudio/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)

            if option == 'audio':
                filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            else:
                filename = ydl.prepare_filename(info_dict)

                if video_format == 'mp4_hd':
                    base, _ = os.path.splitext(filename)
                    output_path = f"{base}_highbitrate.mp4"

                    # Optimización del comando ffmpeg para reducir el bitrate y la carga
                    command = [
                        ffmpeg_path,
                        '-i', filename,
                        '-b:v', '4500k',         # Ajuste de bitrate a 4500 kbps
                        '-maxrate', '4500k',     # Maximo bitrate
                        '-bufsize', '9000k',     # Tamaño de buffer optimizado
                        '-preset', 'fast',       # Menor carga en Railway
                        '-c:a', 'copy',          # Copiar audio sin re-codificar
                        output_path
                    ]

                    subprocess.run(command, check=True)
                    filename = output_path

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"Hubo un problema al descargar o enviar el archivo: {str(e)}", 'error')
        return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
