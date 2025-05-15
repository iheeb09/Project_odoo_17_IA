FROM python:3.10-slim

# Dossier de travail
WORKDIR /app

# Copie requirements
COPY requirements.txt .

# 🛠️ Installation sécurisée des dépendances
RUN apt-get update --allow-releaseinfo-change && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libxrender1 \
    libsm6 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt1-dev \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 🔁 Installation Python (avec timeout long et pytorch CPU)
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    pip install huggingface_hub[hf_xet] && \
    python -m nltk.downloader punkt


# 📁 Copier le code de l'app (selon architecture modulaire)
COPY ./app /app/app

# 🚀 Lancer le serveur API FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8045"]