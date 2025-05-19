from pydantic import BaseModel
from typing import List



# Pour /match/multiple : plusieurs CVs
class CVItem(BaseModel):
    name: str
    text: str

class MatchMultipleRequest(BaseModel):

    job_description: str #Le texte de la description du poste.
    cvs: List[CVItem] #Liste de dictionnaires contenant le nom et le texte de chaque CV.

# Réponse standard
class MatchResult(BaseModel):
    # Liste de dictionnaires avec le nom du CV et le score de similarité,triée par score décroissant


    cv_name: str
    score: float
