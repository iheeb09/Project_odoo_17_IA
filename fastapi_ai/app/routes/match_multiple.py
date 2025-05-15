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
    results = compute_similarity_multiple(
        job_description=request.job_description,
        cvs=[{"name": cv.name, "text": cv.text} for cv in request.cvs]
    )
    return results

