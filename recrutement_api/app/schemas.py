from pydantic import BaseModel, Field
from typing import Literal



class PredictionRequest(BaseModel):
    # Champs catégoriels bruts
    department: str
    # Variables RH de base
    departs_confirmes: float
    candidats_en_cours: float
    postes_ouverts_actuels: float
    effectif_actuel: float
    turnover_month_pct: float


    # Rolling means (window=4 trimestres)
    departs_confirmes_rolling_mean:      float
    candidats_en_cours_rolling_mean:     float
    postes_ouverts_actuels_rolling_mean: float
    effectif_actuel_rolling_mean:        float
    turnover_month_pct_rolling_mean:     float


    # Lags (1 à 4 trimestres)
    departs_confirmes_lag_1:      float
    departs_confirmes_lag_2:      float
    departs_confirmes_lag_3:      float
    departs_confirmes_lag_4:      float

    candidats_en_cours_lag_1:     float
    candidats_en_cours_lag_2:     float
    candidats_en_cours_lag_3:     float
    candidats_en_cours_lag_4:     float

    postes_ouverts_actuels_lag_1: float
    postes_ouverts_actuels_lag_2: float
    postes_ouverts_actuels_lag_3: float
    postes_ouverts_actuels_lag_4: float

    effectif_actuel_lag_1:        float
    effectif_actuel_lag_2:        float
    effectif_actuel_lag_3:        float
    effectif_actuel_lag_4:        float

    turnover_month_pct_lag_1:     float
    turnover_month_pct_lag_2:     float
    turnover_month_pct_lag_3:     float
    turnover_month_pct_lag_4:     float



    # Saison et année
    quarter_num: int
    annee: int
