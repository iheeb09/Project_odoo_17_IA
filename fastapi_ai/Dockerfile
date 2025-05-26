FROM python:3.10-slim

WORKDIR /app

#  Dépendances système nécessaires
RUN apt-get update --allow-releaseinfo-change && apt-get install -y --no-install-recommends \
    build-essential libglib2.0-0 libgl1-mesa-glx libxrender1 libsm6 libxext6 libjpeg-dev \
    zlib1g-dev libxml2-dev libxslt1-dev git curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

#  Mise à jour de pip
RUN pip install --upgrade pip

#  Compatibilité Torch avec NumPy
RUN pip install "numpy<2.0.0"

#  Installation PyTorch CPU
RUN pip install --default-timeout=1000 "torch==2.2.2+cpu" -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Transformers compatible avec torch 2.2.2
RUN pip install "transformers==4.37.2"

#  Sentence Transformers + patch pour Hugging Face
RUN pip install sentence-transformers==2.6.1
RUN pip install "huggingface_hub[hf_xet]"

# Préchargement du modèle Hugging Face pour éviter les délais au démarrage
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Autres dépendances FastAPI
RUN pip install fastapi==0.110.0 uvicorn[standard]==0.29.0 \
    nltk==3.8.1 scikit-learn==1.4.2 python-multipart==0.0.9

# Téléchargement des ressources NLTK nécessaires
RUN python -m nltk.downloader punkt

# Ajout du code de l’application
COPY ./app /app/app

#  Lancement de l’API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8045"]