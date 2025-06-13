import logging
from typing import Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.model import load_model_and_encoder, predict_postes
from app.schemas import PredictionRequest

# Initialisation de FastAPI
app = FastAPI(title="Recruitment Needs Forecast API")

# Globals
pipeline = None
ohe = None
features = None

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Gestion personnalisée des erreurs de validation (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    raw_body = await request.body()
    logging.error(f"Requête invalide sur {request.url}")
    logging.error(f"Corps brut : {raw_body.decode('utf-8')}")
    logging.error(f"Erreurs Pydantic : {exc.errors()}")
    for err in exc.errors():
        if err["type"] == "value_error.missing":
            loc = ".".join(map(str, err["loc"]))
            logging.error(f"Champ manquant : {loc}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Chargement du modèle au démarrage de l'app
@app.on_event("startup")
async def startup_event():
    global pipeline, ohe, features
    try:
        pipeline, ohe, features = load_model_and_encoder()
        logging.info("Modèle et encodeur chargés avec succès.")
    except FileNotFoundError as e:
        logging.critical(f"Erreur de chargement des artefacts : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de chargement des artefacts : {e}"
        )

# Endpoint de prédiction
@app.post("/predict", response_model=Dict[str, float], tags=["Prediction"])
async def predict_endpoint(payload: PredictionRequest):
    """
    Reçoit un payload Pydantic, le convertit en DataFrame,
    et renvoie la prédiction du nombre de postes à lancer.
    """
    try:
        input_df = pd.DataFrame([payload.dict()])
        pred = predict_postes(
            input_df,
            pipeline,
            ohe,
            features
        )
        return {"prediction": pred}

    except KeyError as e:
        logging.error(f"Feature manquante ou invalide : {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Feature manquante ou invalide : {e}"
        )

    except Exception as e:
        logging.error(f"Erreur de prédiction : {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de prédiction : {e}"
        )
