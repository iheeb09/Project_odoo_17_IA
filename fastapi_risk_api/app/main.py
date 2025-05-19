from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict
import pandas as pd
import logging

from app.model import load_model_and_encoder, predict_risk_level
from app.schemas import EmployeeFeatures

# 🎯 Initialisation de l'application FastAPI
app = FastAPI(title="Employee Attrition Prediction API")

# 🔧 Variables globales (chargées au démarrage)
model = None
label_encoder = None

# 🧾 Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🚨 Gestion personnalisée des erreurs de validation (422 Unprocessable Entity)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_body = await request.body()
    logging.error(f"📨 Requête invalide reçue sur : {request.url}")
    logging.error(f"🧾 Corps brut de la requête : {raw_body.decode('utf-8')}")
    logging.error(f"❌ Erreurs détectées : {exc.errors()}")

    # 🎯 Log supplémentaire des champs manquants
    for err in exc.errors():
        if err["type"] == "value_error.missing":
            logging.error(f"🔎 Champ manquant : {'.'.join(map(str, err['loc']))}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# 🚀 Chargement du modèle au démarrage de l'app
@app.on_event("startup")
async def startup_event():
    global model, label_encoder
    try:
        model, label_encoder = load_model_and_encoder()
        logging.info("✅ Modèle et encodeur chargés avec succès.")
    except FileNotFoundError as e:
        logging.critical(f"❌ Erreur de chargement du modèle ou encodeur : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de chargement : {str(e)}")

# 🧠 Route de prédiction principale
@app.post("/predict", response_model=Dict[str, str])
async def predict(employee: EmployeeFeatures):
    try:
        input_df = pd.DataFrame([employee.dict()])
        risk_level = predict_risk_level(input_df, model, label_encoder)
        return {"prediction": risk_level}
    except Exception as e:
        logging.error(f"❌ Erreur de prédiction : {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erreur de prédiction : {str(e)}")
