FROM python:3.10-slim

LABEL maintainer="Germán Vallejo Palma <german.vallejo@isciii.es>"

WORKDIR /opt/app

# Install system deps if needed (e.g., libxml2 for Biopython depending on features)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package and install in editable mode (or pip install from PyPI)
COPY . /opt/app
RUN pip install --no-cache-dir .

ENTRYPOINT ["/bin/bash", "-lc"]
