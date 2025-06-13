from pathlib import Path
import joblib
import pandas as pd
from typing import Tuple, List, Any, Dict
from sklearn.preprocessing import OneHotEncoder

# Chemin absolu vers le dossier model/ (quel que soit le cwd)
MODEL_DIR = Path(__file__).resolve().parents[1] / "model"

def load_model_and_encoder() -> Tuple[
    Any,           # pipeline préprocesseur + modèle
    OneHotEncoder, # encoder pour department
    List[str]      # liste des features
]:
    """
    Charge depuis MODEL_DIR :
      - best_model.pkl    → pipeline (préprocesseur + modèle)
      - ohe_encoder.pkl   → OneHotEncoder pour department
      - features.txt      → liste des colonnes numériques dans l'ordre
    """
    pipeline = joblib.load(MODEL_DIR / "best_model.pkl")
    ohe = joblib.load(MODEL_DIR / "ohe_encoder.pkl")
    # Lecture de l'ordre des features
    with open(MODEL_DIR / "features.txt", encoding="utf-8") as f:
        features = [line.strip() for line in f if line.strip()]
    return pipeline, ohe, features


def predict_postes(
    input_df: pd.DataFrame,
    pipeline: Any,
    ohe: OneHotEncoder,
    features: List[str]
) -> float:
    """
    Prédit le nombre de postes à lancer
    """
    # 1) One-hot encoding de 'department'
    dept_ohe = ohe.transform(input_df[["department"]])
    dept_cols = ohe.get_feature_names_out(["department"])
    df_ohe = pd.DataFrame(dept_ohe, columns=dept_cols, index=input_df.index)
    df_pre = pd.concat([input_df.drop(columns=["department"]), df_ohe], axis=1)

    # 2) Sélection & ordre exact des colonnes
    X = df_pre[features]

    # 3) Prédiction
    y_pred = pipeline.predict(X)
    return int(y_pred[0])
