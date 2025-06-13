# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError

API_URL: str = "http://fastapirecrut:8050/predict"
TIMEOUT: int = 15  # secondes


class DepartmentAnalysisCalculator(models.Model):
    _name = "department.analysis.calculator"
    _description = "Recruitment Need Calculator"

    # ------------------------------------------------------------
    # CONTEXTE & PÉRIODE
    # ------------------------------------------------------------
    department_id = fields.Many2one("hr.department", string="Department", required=True)


    analysis_month = fields.Selection(
        selection=[(str(m), str(m)) for m in range(1, 13)],
        string="Analysis Month",
        required=True,
    )

    analysis_year = fields.Integer(
        string="Analysis Year",
        required=True,
        default=lambda self: datetime.now().year
    )
    date_from = fields.Date(string="From", compute="_compute_analysis_period", store=True)
    date_to = fields.Date(string="To", compute="_compute_analysis_period", store=True)
    # ------------------------------------------------------------
    # (MOIS COURANT)
    # ------------------------------------------------------------
    departs_confirmes = fields.Integer(string="Confirmed Departures", store=True)
    candidats_en_cours = fields.Integer(string="Active Candidates", store=True)
    postes_ouverts_actuels = fields.Integer(string="Open Positions", store=True)
    effectif_actuel = fields.Integer(string="Current Headcount", store=True)
    turnover_month_pct = fields.Float(string="Monthly Turnover Rate", store=True)


    # ----------------------------
    # ROLLING MEAN
    # ----------------------------
    departs_confirmes_rolling_mean = fields.Float(string="Rolling Avg - Confirmed Exits", store=True)
    candidats_en_cours_rolling_mean = fields.Float(string="Rolling Avg - Active Applicants", store=True)
    postes_ouverts_actuels_rolling_mean = fields.Float(string="Rolling Avg - Open Positions", store=True)
    effectif_actuel_rolling_mean = fields.Float(string="Rolling Avg - Total Employees", store=True)
    turnover_month_pct_rolling_mean = fields.Float(string="Rolling Avg - Monthly Attrition Rate", store=True)


    # ----------------------------
    # LAGS 1 → 4 pour chaque champs
    # ----------------------------
    departs_confirmes_lag_1 = fields.Float(string="Lag 1 - Confirmed Exits", store=True)
    departs_confirmes_lag_2 = fields.Float(string="Lag 2 - Confirmed Exits", store=True)
    departs_confirmes_lag_3 = fields.Float(string="Lag 3 - Confirmed Exits", store=True)
    departs_confirmes_lag_4 = fields.Float(string="Lag 4 - Confirmed Exits", store=True)

    candidats_en_cours_lag_1 = fields.Float(string="Lag 1 - Active Applicants", store=True)
    candidats_en_cours_lag_2 = fields.Float(string="Lag 2 - Active Applicants", store=True)
    candidats_en_cours_lag_3 = fields.Float(string="Lag 3 - Active Applicants", store=True)
    candidats_en_cours_lag_4 = fields.Float(string="Lag 4 - Active Applicants", store=True)

    postes_ouverts_actuels_lag_1 = fields.Float(string="Lag 1 - Open Positions", store=True)
    postes_ouverts_actuels_lag_2 = fields.Float(string="Lag 2 - Open Positions", store=True)
    postes_ouverts_actuels_lag_3 = fields.Float(string="Lag 3 - Open Positions", store=True)
    postes_ouverts_actuels_lag_4 = fields.Float(string="Lag 4 - Open Positions", store=True)

    effectif_actuel_lag_1 = fields.Float(string="Lag 1 - Total Employees", store=True)
    effectif_actuel_lag_2 = fields.Float(string="Lag 2 - Total Employees", store=True)
    effectif_actuel_lag_3 = fields.Float(string="Lag 3 - Total Employees", store=True)
    effectif_actuel_lag_4 = fields.Float(string="Lag 4 - Total Employees", store=True)

    turnover_month_pct_lag_1 = fields.Float(string="Lag 1 - Monthly Attrition Rate", store=True)
    turnover_month_pct_lag_2 = fields.Float(string="Lag 2 - Monthly Attrition Rate", store=True)
    turnover_month_pct_lag_3 = fields.Float(string="Lag 3 - Monthly Attrition Rate", store=True)
    turnover_month_pct_lag_4 = fields.Float(string="Lag 4 - Monthly Attrition Rate", store=True)


    # ------------------------------------------------------------
    # CALENDRIER
    # ------------------------------------------------------------
    quarter_num = fields.Integer(string="Quarter", compute="_compute_calendar_indicators", store=True)


    # ------------------------------------------------------------
    # SORTIE DU MODÈLE
    # ------------------------------------------------------------
    predicted_need = fields.Float(string="Predicted Need", readonly=True)

    # ============================================================
    # 1. PÉRIODE D’ANALYSE
    # ============================================================
    @api.depends("analysis_month", "analysis_year")
    def _compute_analysis_period(self):
        for rec in self:
            if rec.analysis_month and rec.analysis_year:
                try:
                    month = int(rec.analysis_month)
                    year = rec.analysis_year
                    # date_to = dernier jour du mois sélectionné
                    last_day = calendar.monthrange(year, month)[1]
                    date_to = date(year, month, last_day)
                    # date_from = date_to moins 3 mois + 1 jour pour couvrir 3 mois complets
                    date_from = date_to + relativedelta(months=-3) + relativedelta(days=1)

                    rec.date_from = date_from
                    rec.date_to = date_to

                except Exception as e:
                    _logger.error("❌ Erreur dans _compute_analysis_period: %s", e)
                    rec.date_from = rec.date_to = False
            else:
                rec.date_from = rec.date_to = False

    # @api.depends("analysis_month", "analysis_year")
    # def _compute_analysis_period(self):
    #     for rec in self:
    #         if rec.analysis_month and rec.analysis_year:
    #             try:
    #                 month = int(rec.analysis_month)
    #                 year = rec.analysis_year
    #                 rec.date_from = date(year, month, 1)
    #                 last_day = calendar.monthrange(year, month)[1]
    #                 rec.date_to = date(year, month, last_day)
    #             except Exception as e:
    #                 _logger.error("❌ Erreur dans _compute_analysis_period: %s", e)
    #                 rec.date_from = rec.date_to = False
    #         else:
    #             rec.date_from = rec.date_to = False

    # ============================================================
    # 2. KPI DE BASE
    # ============================================================
    @api.depends("department_id", "date_from", "date_to")
    def _compute_basic_metrics(self):
        employee = self.env["hr.employee"]
        contract = self.env["hr.contract"]
        applicant = self.env["hr.applicant"]
        job = self.env["hr.job"]
        evaluation = self.env["historique.evaluation"]

        for rec in self:
            # Valeurs par défaut
            rec.departs_confirmes = 0.0
            rec.candidats_en_cours = 0.0
            rec.postes_ouverts_actuels = 0.0
            rec.effectif_actuel = 0.0
            rec.turnover_month_pct = 0.0


            # Effectif actuel
            employees = employee.search([
                ("department_id", "=", rec.department_id.id)
            ])
            rec.effectif_actuel = len(employees)

            # Départs confirmés (contrats terminés + attrition risquée)
            ended_contracts = contract.search_count([
                ("employee_id.department_id", "=", rec.department_id.id),
                # ("date_end", ">=", rec.date_from),
                # ("date_end", "<=", rec.date_to),
                ("state", "=", "close")
            ])
            risky_attrition = evaluation.search_count([
                ("employee_id.department_id", "=", rec.department_id.id),
                ("date", ">=", rec.date_from),
                ("date", "<=", rec.date_to),
                ("pred_risk", "=", "high"),
            ])
            rec.departs_confirmes = ended_contracts + risky_attrition
            # Turnover mensuel (%)
            if rec.effectif_actuel:
                rec.turnover_month_pct = (
                    rec.departs_confirmes / rec.effectif_actuel
                )

            # Pipeline candidats
            jobs = job.search([
                ("department_id", "=", rec.department_id.id)
            ])
            rec.candidats_en_cours = applicant.search_count([
                ("job_id", "in", jobs.ids),
                ("application_status", "=", "ongoing"),
            ])

            # Calcul des postes ouverts (correct)
            open_positions = 0.0
            for job in jobs:
                open_positions += job.no_of_recruitment or 0.0
            rec.postes_ouverts_actuels = open_positions


    # ============================================================
    # 3. QUARTER
    # ============================================================
    @api.depends("analysis_month")
    def _compute_calendar_indicators(self):
        for rec in self:
            if rec.analysis_month:
                month = int(rec.analysis_month)
                rec.quarter_num = (month - 1) // 3 + 1
            else:
                rec.quarter_num = False

    # ============================================================
    # 4. HISTORIQUE
    # ============================================================
    def _compute_history_features(self):
        History = self.env["department.analysis.history"]
        #calculer le mois et l'année de période précédente (pour lag1 => mois=ce mois-1 si decembre on passe à l'anne derniere)
        def previous_month(month: int, year: int, steps_back: int):
            for _ in range(steps_back):
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            return month, year

        metric_list = [
            "departs_confirmes",
            "candidats_en_cours",
            "postes_ouverts_actuels",
            "effectif_actuel",
            "turnover_month_pct",

        ]

        for rec in self:
            month_int = int(rec.analysis_month)
            year_int = rec.analysis_year

            for metric in metric_list:
                # ----- Rolling mean -----
                rolling_sum = 0.0
                for idx in range(4):
                    m, y = previous_month(month_int, year_int, idx)
                    hist_rec = History.search([
                        ("department_id", "=", rec.department_id.id),
                        ("analysis_month", "=", str(m)),
                        ("analysis_year", "=", y),
                    ], limit=1)
                    value = getattr(hist_rec, metric, 0.0) if hist_rec else 0.0
                    rolling_sum += value
                rolling_mean = rolling_sum / 4
                setattr(rec, f"{metric}_rolling_mean", rolling_mean)

                # ----- Lags 1 à 4 -----
                for lag in range(1, 5):
                    m, y = previous_month(month_int, year_int, lag)
                    hist_rec = History.search([
                        ("department_id", "=", rec.department_id.id),
                        ("analysis_month", "=", str(m)),
                        ("analysis_year", "=", y),
                    ], limit=1)
                    #si lag=1 => m=4 (juin=5) =>recuperer les valeurs de mois precedent(mai)
                    lag_value = getattr(hist_rec, metric, 0.0) if hist_rec else 0.0
                    #effectue ces valeurs au rec.metric_lag_1
                    setattr(rec, f"{metric}_lag_{lag}", lag_value)

    # ============================================================
    # 5. ACTION : PREDICTION + HISTORISATION
    # ============================================================
    def action_calculate_prediction(self, _logger=None):
        """En un clic : appelle l’API FastAPI prédit le besoin puis l’enregistre dans l’historique ."""

        # S’assurer que l’action est exécutée sur un seul enregistrement
        self.ensure_one()
        # Met à jour calcul
        self._compute_basic_metrics()
        # Vérification des attributs avant utilisation
        if not self.department_id or not self.date_from or not self.date_to:
            raise UserError(_("Données manquantes: département ou dates non définis"))
        # Met à jour l’historique avant l’envoi
        self._compute_history_features()

        # ------------------------------------------------------------------
        # 1) BASE DU PAYLOAD
        # ------------------------------------------------------------------
        base_values: dict[str, float | str | int] = {
            "department": self.department_id.name or "",
            # KPI de base
            "departs_confirmes": self.departs_confirmes,
            "candidats_en_cours": self.candidats_en_cours,
            "postes_ouverts_actuels": self.postes_ouverts_actuels,
            "effectif_actuel": self.effectif_actuel,
            "turnover_month_pct": self.turnover_month_pct,

            # Rolling means (fenêtre = 4 trimestres)
            "departs_confirmes_rolling_mean": self.departs_confirmes_rolling_mean,
            "candidats_en_cours_rolling_mean": self.candidats_en_cours_rolling_mean,
            "postes_ouverts_actuels_rolling_mean": self.postes_ouverts_actuels_rolling_mean,
            "effectif_actuel_rolling_mean": self.effectif_actuel_rolling_mean,
            "turnover_month_pct_rolling_mean": self.turnover_month_pct_rolling_mean,

            # Calendrier
            "quarter_num": self.quarter_num,
            "annee": self.analysis_year,
        }

        # ------------------------------------------------------------------
        # 2) LAGS 1 → 4
        # ------------------------------------------------------------------
        lag_values: dict[str, float] = {}
        for lag in range(1, 5):
            # Départs confirmés
            lag_values[f"departs_confirmes_lag_{lag}"] = getattr(self, f"departs_confirmes_lag_{lag}") or 0.0
            # Candidats en cours
            lag_values[f"candidats_en_cours_lag_{lag}"] = getattr(self, f"candidats_en_cours_lag_{lag}") or 0.0
            # Postes ouverts
            lag_values[f"postes_ouverts_actuels_lag_{lag}"] = getattr(self, f"postes_ouverts_actuels_lag_{lag}") or 0.0
            # Effectif actuel
            lag_values[f"effectif_actuel_lag_{lag}"] = getattr(self, f"effectif_actuel_lag_{lag}") or 0.0
            # Turnover mensuel
            lag_values[f"turnover_month_pct_lag_{lag}"] = getattr(self, f"turnover_month_pct_lag_{lag}") or 0.0


        # ------------------------------------------------------------------
        # 3) FUSION DES DICTIONNAIRES (méthode classique)
        # ------------------------------------------------------------------
        payload: dict[str, float | str | int] = {}
        payload.update(base_values)
        payload.update(lag_values)

        # ------------------------------------------------------------------
        # 4) APPEL HTTP → FASTAPI
        # ------------------------------------------------------------------
        # 3) Appeler l’API FastAPI
        try:
            response = requests.post(API_URL, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            result = response.json()
            self.predicted_need = int(result.get("prediction", 0.0))
        except Exception as exc:
            raise UserError(_("Prediction failed: %s") % str(exc))

        # 4) Sauvegarder ou mettre à jour l’historique
        self.action_save_history()
    # ------------------------------------------------------------
    # Méthode d’historisation appelée juste après la prédiction
    # ------------------------------------------------------------
    def action_save_history(self):
        """Crée ou met à jour la ligne du trimestre dans department.analysis.history."""
        self.ensure_one()
        History = self.env["department.analysis.history"]

        # Chercher si l’enregistrement existe déjà
        existing = History.search([
            ("department_id", "=", self.department_id.id),
            ("analysis_month", "=", self.analysis_month),
            ("analysis_year", "=", self.analysis_year),
        ], limit=1)

        vals = {
            "department_id": self.department_id.id,
            "analysis_month": self.analysis_month,
            "analysis_year": self.analysis_year,
            "date_from": self.date_from,
            "date_to": self.date_to,
            # KPI de base
            "departs_confirmes": self.departs_confirmes,
            "candidats_en_cours": self.candidats_en_cours,
            "postes_ouverts_actuels": self.postes_ouverts_actuels,
            "effectif_actuel": self.effectif_actuel,
            "turnover_month_pct": self.turnover_month_pct,

            # Rolling means
            "departs_confirmes_rolling_mean": self.departs_confirmes_rolling_mean,
            "candidats_en_cours_rolling_mean": self.candidats_en_cours_rolling_mean,
            "postes_ouverts_actuels_rolling_mean": self.postes_ouverts_actuels_rolling_mean,
            "effectif_actuel_rolling_mean": self.effectif_actuel_rolling_mean,
            "turnover_month_pct_rolling_mean": self.turnover_month_pct_rolling_mean,
            # Lags 1→4
            "departs_confirmes_lag_1": self.departs_confirmes_lag_1,
            "departs_confirmes_lag_2": self.departs_confirmes_lag_2,
            "departs_confirmes_lag_3": self.departs_confirmes_lag_3,
            "departs_confirmes_lag_4": self.departs_confirmes_lag_4,
            "candidats_en_cours_lag_1": self.candidats_en_cours_lag_1,
            "candidats_en_cours_lag_2": self.candidats_en_cours_lag_2,
            "candidats_en_cours_lag_3": self.candidats_en_cours_lag_3,
            "candidats_en_cours_lag_4": self.candidats_en_cours_lag_4,
            "postes_ouverts_actuels_lag_1": self.postes_ouverts_actuels_lag_1,
            "postes_ouverts_actuels_lag_2": self.postes_ouverts_actuels_lag_2,
            "postes_ouverts_actuels_lag_3": self.postes_ouverts_actuels_lag_3,
            "postes_ouverts_actuels_lag_4": self.postes_ouverts_actuels_lag_4,
            "effectif_actuel_lag_1": self.effectif_actuel_lag_1,
            "effectif_actuel_lag_2": self.effectif_actuel_lag_2,
            "effectif_actuel_lag_3": self.effectif_actuel_lag_3,
            "effectif_actuel_lag_4": self.effectif_actuel_lag_4,
            "turnover_month_pct_lag_1": self.turnover_month_pct_lag_1,
            "turnover_month_pct_lag_2": self.turnover_month_pct_lag_2,
            "turnover_month_pct_lag_3": self.turnover_month_pct_lag_3,
            "turnover_month_pct_lag_4": self.turnover_month_pct_lag_4,

            # Calendrier et prédiction
            "quarter_num": self.quarter_num,
            "predicted_need": self.predicted_need,
        }

        if existing:
            existing.write(vals)
        else:
            History.create([vals])