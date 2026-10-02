# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para GUI (Tkinter) y gráficos (OpenGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    libxrender1 \
    libxext6 \
    libsm6 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Ejecutar la aplicación
CMD ["python", "main.py"]