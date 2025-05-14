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
    video_format = request.form['format']  # mp3 / mp4 / mp4_hd / webm

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
            # Para video primero extraemos info sin descargar para saber si hay video con tbr>2500
            with YoutubeDL({'quiet': True}) as ydl_check:
                info = ydl_check.extract_info(url, download=False)

            # Buscamos si hay video con tbr > 2500 y ext mp4, height <=1080
            has_high_tbr = False
            formats = info.get('formats', [])
            for f in formats:
                if (f.get('ext') == 'mp4' and
                    f.get('height') is not None and f.get('height') <= 1080 and
                    f.get('tbr') is not None and f.get('tbr') > 2500 and
                    f.get('vcodec') != 'none'):
                    has_high_tbr = True
                    break

            # Definimos opciones segun formato y si hay high tbr
            if video_format == 'mp4':
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best',
                    'ffmpeg_location': ffmpeg_path,
                    'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    }],
                }
            elif video_format == 'mp4_hd':
                if has_high_tbr:
                    # Descargar con filtro bitrate alto
                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4][height<=1080][tbr>2500]+bestaudio[ext=m4a]/best',
                        'ffmpeg_location': ffmpeg_path,
                        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4'
                        }],
                    }
                else:
                    flash('No se encontró video con bitrate alto (>2500 tbr). Descargando mejor calidad disponible.', 'warning')
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
            else:
                flash('Formato de video no soportado.', 'error')
                return render_template('index.html')

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"Hubo un problema al descargar o enviar el archivo: {str(e)}", 'error')
        return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
