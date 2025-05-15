# 🐍 Étend l’image officielle Odoo 17
FROM odoo:17

USER root

# 🛠️ Installation des dépendances système + PyMuPDF (fitz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1-mesa-glx \
    python3-dev \
    gcc \
    && pip install --no-cache-dir --timeout=1000 PyMuPDF \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER odoo
