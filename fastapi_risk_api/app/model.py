import joblib
from pathlib import Path
import pandas as pd


# Configuration
MODEL_DIR = Path("model")
MODEL_PATH = MODEL_DIR / "final_model.pkl"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"

def load_model_and_encoder():
    """Charge le modèle XGBoost et le LabelEncoder."""
    try:
        model = joblib.load(MODEL_PATH)
        label_encoder = joblib.load(LABEL_ENCODER_PATH)
        return model, label_encoder
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Modèle ou encodeur non trouvé à {MODEL_PATH} ou {LABEL_ENCODER_PATH}")

def predict_risk_level(input_data: pd.DataFrame, model, label_encoder):
    """Prédit le Risk_Level pour les données d'entrée."""
    # Normalisation des noms de colonnes
    input_data.columns = input_data.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
    
    # Prédiction
    pred = model.predict(input_data)[0]
    risk_level = label_encoder.inverse_transform([pred])[0]
    return risk_level
