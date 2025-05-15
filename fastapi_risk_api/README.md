Employee Attrition Prediction API
API FastAPI pour prédire le niveau de risque d'attrition des employés à l'aide d'un modèle XGBoost multiclasse. Intégrée avec Odoo via l'endpoint /predict.
Structure du projet
fastapi_risk_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   ├── utils.py
│   ├── schemas.py
├── model/
│   ├── final_model.pkl
│   ├── label_encoder.pkl
├── data/
│   └── train_with_risk.csv
├── requirements.txt
├── README.md
├── train_model.py

Prérequis

Python 3.8+
Les fichiers final_model.pkl et label_encoder.pkl doivent être présents dans model/.
Le fichier train_with_risk.csv doit être dans data/.

Installation

Clonez le répertoire :git clone <repository>
cd fastapi_risk_api


Créez un environnement virtuel :python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Installez les dépendances :pip install -r requirements.txt



Entraînement du modèle

Placez train_with_risk.csv et test_with_predictions.csv dans data/.
Exécutez le script d'entraînement :python train_model.py


Les fichiers final_model.pkl et label_encoder.pkl seront générés dans model/.

Exécution de l'API

Lancez l'API :uvicorn app.main:app --host 0.0.0.0 --port 8001


Accédez à la documentation interactive : http://localhost:8001/docs

Endpoints

POST /predict : Prédit le Risk_Level pour un employé.
Exemple de requête :{
    "age": 35,
    "years_at_company": 5,
    "job_role": "Software Engineer",
    "monthly_income": 5000,
    "distance_from_home": 10,
    "number_of_promotions": 2,
    "number_of_dependents": 1,
    "company_tenure": 10,
    "job_level": "Mid",
    "company_size": "Large",
    "education_level": "Bachelor’s Degree",
    "marital_status": "Married",
    "overtime": "No",
    "remote_work": "Yes",
    "leadership_opportunities": "No",
    "innovation_opportunities": "Yes",
    "gender": "Male",
    "company_reputation": "Good",
    "employee_recognition": "Medium",
    "work_life_balance": "Good",
    "job_satisfaction": "High",
    "performance_rating": "Average"
}


Réponse :{"prediction": "Low"}


Intégration avec Odoo

Le module Odoo fields.py appelle l'endpoint /predict à http://fastapi:8001/predict.
Assurez-vous que le conteneur FastAPI est accessible depuis Odoo (par exemple, via Docker avec un réseau commun).
Le champ predicted_risk dans hr.employee stocke le résultat.

Notes

Les valeurs des champs catégoriels doivent correspondre à celles définies dans schemas.py.
Le modèle utilise un mappage : Low=0, Medium=1, High=2.
