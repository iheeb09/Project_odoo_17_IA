import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes import match_multiple

# Configuration du logger
logging.basicConfig(level=logging.INFO)

# Création de l'application FastAPI
app = FastAPI(
    title="API Matching IA RH",
    description="Compare des CVs à des descriptions de poste pour aider au recrutement",
    version="1.0.0"
)

# Gestion personnalisée des erreurs de validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_body = await request.body()

    logging.error(f"Requête invalide sur : {request.url}")
    logging.error(f"Contenu brut : {raw_body.decode('utf-8')}")
    logging.error(f"Erreurs de validation : {exc.errors()}")

    for err in exc.errors():
        if err["type"] == "value_error.missing":
            field_path = ".".join(map(str, err["loc"]))
            logging.error(f"Champ manquant : {field_path}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Inclusion des routes
app.include_router(match_multiple.router)

# Endpoint de vérification de l'état de l'API
@app.get("/healthcheck")
def healthcheck():
    return {"status": "API opérationnelle "}
