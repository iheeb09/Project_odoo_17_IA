FROM python:3.10-slim
#Définir le répertoire de travail
# Pour voir les logs en temps réel
ENV PYTHONUNBUFFERED=1
WORKDIR /app
#Copier les fichiers de dépendances

COPY requirements.txt .
#Installer les dépendances

RUN pip install --no-cache-dir -r requirements.txt
#Copier le code source, les modèles et les données

COPY app/ ./app/
COPY model/ ./model/

#Exposer le port 8020

EXPOSE 8020
#Commande pour lancer l'API

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
