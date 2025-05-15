from pydantic import BaseModel
from typing import List

# Pour /match : un seul CV
class MatchRequest(BaseModel):
    cv_text: str
    job_description: str

# Pour /match/multiple : plusieurs CVs
class CVItem(BaseModel):
    name: str
    text: str

class MatchMultipleRequest(BaseModel):
    job_description: str
    cvs: List[CVItem]

# Réponse standard
class MatchResult(BaseModel):
    cv_name: str
    score: float
