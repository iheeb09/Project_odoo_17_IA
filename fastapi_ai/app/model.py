from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Chargement du modèle multilingue pour générer des embeddings de phrases
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


# Compare une description de poste à plusieurs CVs
def compute_similarity_multiple(job_description: str, cvs: list[dict]) -> list[dict]:
    """
    Compare une description de poste à une liste de CVs (textes),
    en utilisant la similarité cosinus sur des embeddings de phrases.


    """

    # Initialisation des listes de noms et de textes
    texts = []
    names = []

    # Extraction des textes et noms des CVs
    for cv in cvs:
        texts.append(cv["text"])
        names.append(cv["name"])

    # Encodage de la description du poste
    job_embedding = model.encode([job_description])[0]

    # Encodage des CVs
    cv_embeddings = model.encode(texts)

    # Calcul des similarités cosinus entre la description du poste et chaque CV
    similarities = cosine_similarity([job_embedding], cv_embeddings)[0]

    # Construction des résultats avec score
    results = []
    for i in range(len(names)):
        result = {
            "cv_name": names[i],
            "score": float(similarities[i])
        }
        results.append(result)

    # Fonction pour extraire le score de chaque résultat
    def get_score(item):
        return item["score"]

    # Tri des résultats par score décroissant
    results.sort(key=get_score, reverse=True)

    return results
