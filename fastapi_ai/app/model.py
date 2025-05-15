from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 🧠 Chargement du modèle multilingue
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def compute_similarity(cv_text: str, job_description: str) -> float:
    embeddings = model.encode([cv_text, job_description])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(sim)

def compute_similarity_multiple(job_description: str, cvs: list[dict]) -> list[dict]:
    texts = [cv["text"] for cv in cvs]
    names = [cv["name"] for cv in cvs]

    job_embedding = model.encode([job_description])[0]
    cv_embeddings = model.encode(texts)

    similarities = cosine_similarity([job_embedding], cv_embeddings)[0]

    results = [
        {"cv_name": names[i], "score": float(similarities[i])}
        for i in range(len(names))
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
