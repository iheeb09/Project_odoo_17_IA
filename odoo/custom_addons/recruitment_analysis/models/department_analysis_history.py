from datetime import datetime
from odoo import models, fields, api, _


class DepartmentAnalysisHistory(models.Model):
    _name = "department.analysis.history"
    _description = "Recruitment Analysis History"


    # ------------------------------------------------------------------

    department_id = fields.Many2one("hr.department", required=True)
    analysis_month = fields.Selection([(str(m), str(m)) for m in range(1, 13)], required=True)
    analysis_year = fields.Integer()

    date_from = fields.Date(string="From",store=True)
    date_to = fields.Date(string="To", store=True)

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    departs_confirmes = fields.Integer(string="Confirmed Departures", store=True)
    candidats_en_cours = fields.Integer(string="Candidates", store=True)
    postes_ouverts_actuels = fields.Integer(string="Open Positions", store=True)
    effectif_actuel = fields.Integer(string="Current Headcount", store=True)
    turnover_month_pct = fields.Float(string="Monthly Turnover Rate", store=True)


    # ----------------------------
    # ROLLING MEAN
    # ----------------------------
    departs_confirmes_rolling_mean = fields.Float(string="AvgConfirmed Departures", store=True)
    candidats_en_cours_rolling_mean = fields.Float(string="AvgCandidates", store=True)
    postes_ouverts_actuels_rolling_mean = fields.Float(string="AvgOpen Positions", store=True)
    effectif_actuel_rolling_mean = fields.Float(string="AvgTotal Employees", store=True)
    turnover_month_pct_rolling_mean = fields.Float(string="AvgMonthly Turnover Rate", store=True)


    # ----------------------------
    # LAGS 1 → 4 pour chaque champs
    # ----------------------------
    departs_confirmes_lag_1 = fields.Float(string="Confirmed Departures-1", store=True)
    departs_confirmes_lag_2 = fields.Float(string="Confirmed Departures-2", store=True)
    departs_confirmes_lag_3 = fields.Float(string="Confirmed Departures-3", store=True)
    departs_confirmes_lag_4 = fields.Float(string="Confirmed Departures-4", store=True)

    candidats_en_cours_lag_1 = fields.Float(string="Candidates-1", store=True)
    candidats_en_cours_lag_2 = fields.Float(string="Lag 2 - Candidates", store=True)
    candidats_en_cours_lag_3 = fields.Float(string="Lag 3 - Candidates", store=True)
    candidats_en_cours_lag_4 = fields.Float(string="Lag 4 - Candidates", store=True)

    postes_ouverts_actuels_lag_1 = fields.Float(string="Lag 1 - Open Positions", store=True)
    postes_ouverts_actuels_lag_2 = fields.Float(string="Lag 2 - Open Positions", store=True)
    postes_ouverts_actuels_lag_3 = fields.Float(string="Lag 3 - Open Positions", store=True)
    postes_ouverts_actuels_lag_4 = fields.Float(string="Lag 4 - Open Positions", store=True)

    effectif_actuel_lag_1 = fields.Float(string="Lag 1 - Total Employees", store=True)
    effectif_actuel_lag_2 = fields.Float(string="Lag 2 - Total Employees", store=True)
    effectif_actuel_lag_3 = fields.Float(string="Lag 3 - Total Employees", store=True)
    effectif_actuel_lag_4 = fields.Float(string="Lag 4 - Total Employees", store=True)

    turnover_month_pct_lag_1 = fields.Float(string="Lag 1 - Monthly Turnover Rate", store=True)
    turnover_month_pct_lag_2 = fields.Float(string="Lag 2 - Monthly Turnover Rate", store=True)
    turnover_month_pct_lag_3 = fields.Float(string="Lag 3 - Monthly Turnover Rate", store=True)
    turnover_month_pct_lag_4 = fields.Float(string="Lag 4 - Monthly Turnover Rate", store=True)



    # ------------------------------------------------------------
    # CALENDRIER
    # ------------------------------------------------------------
    quarter_num = fields.Integer(string="Quarter", store=True)

    # ------------------------------------------------------------
    # SORTIE DU MODÈLE
    # ------------------------------------------------------------
    predicted_need = fields.Float(string="Predicted Need", readonly=True)

