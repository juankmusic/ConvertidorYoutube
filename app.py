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
    video_format = request.form['format']  # Obtenemos el formato elegido por el usuario

    # Configuración de yt-dlp para descargar según la opción elegida
    if option == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Cambiar calidad del mp3
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        }
    else:
        # Aquí seleccionamos la mejor calidad de video disponible hasta 1080p
        if video_format == 'mp4':
            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best',
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',  # Esto le dice a yt-dlp que use ffmpeg para unir
                'postprocessors': [{
                    'key': 'FFmpegMerger'
                }],
            }

        elif video_format == 'webm':
            ydl_opts = {
                'format': 'bestvideo[ext=webm][height<=1080]+bestaudio/best',  # Solo hasta 1080p en webm
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)

            if option == 'audio':
                filename = os.path.join(download_folder, f"{info_dict['title']}.mp3")
            else:
                filename = os.path.join(download_folder, f"{info_dict['title']}.{video_format}")  # Utilizamos el formato elegido

        return send_file(filename, as_attachment=True)

    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        print("Error en descarga:", e)
        return render_template('index.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

