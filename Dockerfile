# Imagen base ligera con Python 3.10
FROM python:3.10-slim

LABEL maintainer="German Vallejo <german.vallejo@isciii.es>"
LABEL description="Docker image for mixedassembly v0.1.4"
LABEL version="0.1.4"

# Evita .pyc y mejora logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH"

# Instala dependencias del sistema necesarias para parquet y compilación ligera
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libz-dev \
        libbz2-dev \
        liblzma-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala el paquete desde PyPI
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir mixedassembly==0.1.4

# Define el comando por defecto
ENTRYPOINT ["mixedassembly"]
CMD ["--help"]

