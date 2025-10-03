# Imagen base ligera con Python
FROM python:3.10-slim

# Evita la creación de .pyc y buffer en stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependencias del sistema (ej: compresión, parquet, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libz-dev \
        && rm -rf /var/lib/apt/lists/*

# Instala tu paquete desde PyPI (reemplaza con la versión que publiques)
RUN pip install --no-cache-dir mixedassembly==0.1.3

# Establece el comando por defecto (CLI principal)
ENTRYPOINT ["mixedassembly"]

# Si alguien quiere ver ayuda por defecto
CMD ["--help"]
