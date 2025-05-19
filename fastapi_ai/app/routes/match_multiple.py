from fastapi import APIRouter
from app.schemas import MatchMultipleRequest, MatchResult
from app.model import compute_similarity_multiple

router = APIRouter()

@router.post("/match/multiple", response_model=list[MatchResult])
def match_multiple(request: MatchMultipleRequest):
    """
    Compare une description de poste à une liste de CVs (texte déjà extrait),
    et retourne les scores de similarité triés.
    """

    # Construction de la liste des CVs au format attendu
    cvs_data = []
    for cv in request.cvs:
        cvs_data.append({
            "name": cv.name,
            "text": cv.text
        })

    # Calcul de la similarité
    results = compute_similarity_multiple(
        job_description=request.job_description,
        cvs=cvs_data
    )

    return results
