import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes import  match_multiple

# Configuration logger (optionnel : à adapter selon besoin)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API Matching IA RH",
    description="Compare des CVs à des descriptions de poste pour aider au recrutement",
    version="1.0.0"
)

# 🎯 Gestion personnalisée des erreurs de validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_body = await request.body()
    logging.error(f"📨 Requête invalide reçue sur : {request.url}")
    logging.error(f"🧾 Corps brut de la requête : {raw_body.decode('utf-8')}")
    logging.error(f"❌ Erreurs détectées : {exc.errors()}")

    # 🎯 Détail des champs manquants
    for err in exc.errors():
        if err["type"] == "value_error.missing":
            logging.error(f"🔎 Champ manquant : {'.'.join(map(str, err['loc']))}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Routes de l'API

app.include_router(match_multiple.router)

@app.get("/healthcheck")
def healthcheck():
    return {"status": "API opérationnelle ✅"}
