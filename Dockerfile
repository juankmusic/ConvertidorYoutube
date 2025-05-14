# Imagen base con Python
FROM python:3.11-slim

# Instala ffmpeg y dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (usado por Railway)
EXPOSE 5000

# Comando para correr la app
CMD ["python", "app.py"]
