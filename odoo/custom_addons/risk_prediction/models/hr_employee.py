# -*- coding: utf-8 -*-

import logging
import requests
from collections import defaultdict
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    # ----------------------------------------------------------------

    progress_bar = fields.Integer(string="Risk", compute='_compute_progresse_bar', store=False)

    @api.depends('predicted_risk')
    def _compute_progresse_bar(self):
        for rec in self:
            if rec.predicted_risk == "low":
                rec.progress_bar = 30
            elif rec.predicted_risk == "medium":
                rec.progress_bar = 60
            elif rec.predicted_risk == "high":
                rec.progress_bar = 100
            else:
                rec.progress_bar = 0

    progress_html = fields.Html(
        compute="_compute_progress_html", sanitize=False, string="Risk Progress", readonly=True
    )

    @api.depends('predicted_risk', 'progress_bar')
    def _compute_progress_html(self):
        for record in self:
            color = {
                'high': 'bg-danger',
                'medium': 'bg-warning',
                'low': 'bg-success'
            }.get(record.predicted_risk, 'bg-secondary')

            value = record.progress_bar or 0
            record.progress_html = f"""
                      <div class="progress" style="height: 25px;">
                          <div class="progress-bar {color}" role="progressbar"
                               style="width: {value}%; min-width: 20px;">
                              {value:.0f}%
                          </div>
                      </div>
                  """

    # ------------------------------------------------------------------
    #
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    years_at_company = fields.Integer(string="Years at Company", compute='_compute_years_at_company')
    company_size = fields.Integer(string="Company Size", compute='_compute_company_size')
    work_hours_week = fields.Float(string="Work Hours per Week", compute='_compute_work_hours_week')
    overTime = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="OverTime", compute='_compute_work_hours_week'
    )
    job_level = fields.Selection(
        [('entry', 'Entry'), ('mid', 'Mid'), ('senior', 'Senior')],
        string="Job Level", compute='_compute_job_level'
    )
    remote_work = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Remote Work", compute='_compute_remote_work'
    )
    contract_status = fields.Selection(
        [('new', 'New'), ('running', 'Running'), ('expired', 'Expired')],
        string="Contract Status", compute='_compute_contract_status', store=True
    )
    number_of_promotions = fields.Integer(string="Number of Promotions", compute='_compute_number_of_promotions')
    monthly_income = fields.Float(string="Monthly Income", compute='_compute_monthly_income', store=True)

    # ------------------------------------------------------------------
    # Champs d’évaluation RH (mis à jour par le sondage)
    job_satisfaction = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('very_high', 'Very High'),
        ],
        string="Job Satisfaction",
        store=True,
    )
    work_life_balance = fields.Selection(
        [
            ('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('excellent', 'Excellent')
        ],
        string="Work-Life Balance"
    )
    performance_rating = fields.Selection(
        [('low', 'Low'), ('below_average', 'Below Average'),
         ('average', 'Average'), ('high', 'High')],
        string="Performance Rating"
    )
    leadership_opportunities = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Leadership Opportunities"
    )
    innovation_opportunities = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Innovation Opportunities"
    )
    company_reputation = fields.Selection(
        [('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('excellent', 'Excellent')],
        string="Company Reputation"
    )
    employee_recognition = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('very_high', 'Very High')],
        string="Employee Recognition"
    )

    #  Risque prédit via FastAPI
    predicted_risk = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('undefined', 'Undefined')],
        string="Predicted Risk", readonly=True
    )

    historic_detaill = fields.One2many('historique.evaluation', 'historic_id', string='Historic', invisible="1")
    # ==================================================================
    # Champs numériques totaux
    job_satisfaction_total = fields.Float(string='Total Job Satisfaction Score', readonly=True)
    work_life_balance_total = fields.Float(string='Total Work-Life Balance Score', readonly=True)
    leadership_opportunities_total = fields.Float(string='Total Leadership Opportunities Score', readonly=True)
    innovation_opportunities_total = fields.Float(string='Total Innovation Opportunities Score', readonly=True)
    company_reputation_total = fields.Float(string='Total Company Reputation Score', readonly=True)
    employee_recognition_total = fields.Float(string='Total Employee Recognition Score', readonly=True)

    def write_survey_scores(self, updates):
        """
        Écrit les scores passés dans `updates` et poste un message dans le chatter.

        """
        for employee in self:
            if not updates:
                continue
            employee.sudo().write(updates)
    # ==================================================================

    @api.depends('birthday')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            rec.age = today.year - rec.birthday.year if rec.birthday else 0

    # ------------------------------------------------------------------
    @api.depends('contract_id.date_start', 'contract_id.date_end')
    def _compute_years_at_company(self):
        today = date.today()
        for rec in self:
            start = rec.contract_id.date_start
            end = rec.contract_id.date_end or today
            rec.years_at_company = relativedelta(end, start).years if start else 0

    # ------------------------------------------------------------------
    @api.depends('company_id')
    def _compute_company_size(self):
        for rec in self:
            rec.company_size = self.env['hr.employee'].search_count([
                ('company_id', '=', rec.company_id.id)
            ]) if rec.company_id else 0

    # ------------------------------------------------------------------
    @api.depends('attendance_ids.check_in', 'attendance_ids.check_out')
    def _compute_work_hours_week(self):
        today = date.today()
        start_week = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end_week = start_week + timedelta(days=7)

        attendances = self.env['hr.attendance'].search([
            ('check_in', '>=', start_week),
            ('check_out', '<=', end_week),
            ('check_out', '!=', False),
        ])

        hrs = defaultdict(float)
        for att in attendances:
            hrs[att.employee_id.id] += (att.check_out - att.check_in).total_seconds() / 3600

        for rec in self:
            h = round(hrs.get(rec.id, 0.0), 2)
            rec.work_hours_week = h
            rec.overTime = 'yes' if h > 45.0 else 'no'

    # ------------------------------------------------------------------
    @api.depends('work_location_id')
    def _compute_remote_work(self):
        for rec in self:
            loc = (rec.work_location_id.name or '').lower()
            rec.remote_work = 'yes' if loc in ('home', 'remote') else 'no'

    # ------------------------------------------------------------------
    @api.depends('contract_id.date_start')
    def _compute_job_level(self):
        today = date.today()
        for rec in self:
            start = rec.contract_id.date_start
            yrs = (today - start).days // 365 if start else 0
            rec.job_level = 'entry' if yrs <= 2 else 'mid' if yrs <= 6 else 'senior'

    # ------------------------------------------------------------------
    @api.depends('contract_id.date_start', 'contract_id.date_end')
    def _compute_contract_status(self):
        today = date.today()
        for rec in self:
            start, end = rec.contract_id.date_start, rec.contract_id.date_end
            if start and start > today:
                rec.contract_status = 'new'
            elif start and (not end or end >= today):
                rec.contract_status = 'running'
            elif end and end < today:
                rec.contract_status = 'expired'

    # ------------------------------------------------------------------
    @api.depends('contract_ids')
    def _compute_number_of_promotions(self):
        for rec in self:
            jobs = [c.job_id.id for c in rec.contract_ids if c.job_id]
            rec.number_of_promotions = max(len(set(jobs)) - 1, 0)

    # ------------------------------------------------------------------
    @api.depends('contract_id.wage')
    def _compute_monthly_income(self):
        for rec in self:
            rec.monthly_income = rec.contract_id.wage if rec.contract_id else 0.0

    # ==================================================================
    #  Endpoint FastAPI
    # ------------------------------------------------------------------
    def predict_risk_for_employees(self):
        """
        Appelle le service FastAPI 'http://fastapir:8020/predict'
        et met à jour le champ predicted_risk.
        """
        url = "http://fastapir:8020/predict"
        valid_keys = [k for k, _ in self._fields['predicted_risk'].selection]

        for rec in self:
            payload = {
                "age": rec.age or 0,
                "years_at_company": rec.years_at_company or 0,
                "job_role": rec.department_id.name or "Unknown",
                "monthly_income": int(rec.monthly_income or 0),
                "number_of_promotions": rec.number_of_promotions or 0,
                "distance_from_home": int(rec.km_home_work or 0),
                "number_of_dependents": rec.children or 0,
                "job_level": rec.job_level.capitalize() if rec.job_level else "Mid",
                "company_size": self._get_company_size_label(rec.company_size),
                "education_level": self._map_certificate_to_level(rec.certificate),
                "marital_status": (rec.marital.capitalize() if rec.marital else "Single"),
                "overtime": "Yes" if rec.overTime == "yes" else "No",
                "remote_work": "Yes" if rec.remote_work == "yes" else "No",
                "leadership_opportunities": self._label_or_default(rec.leadership_opportunities, "No"),
                "innovation_opportunities": self._label_or_default(rec.innovation_opportunities, "No"),
                "gender": self._label_or_default(rec.gender, "Male"),
                "company_reputation": self._label_or_default(rec.company_reputation, "Good"),
                "employee_recognition": self._label_or_default(rec.employee_recognition, "Medium"),
                "work_life_balance": self._label_or_default(rec.work_life_balance, "Fair"),
                "job_satisfaction": self._label_or_default(rec.job_satisfaction, "Medium"),
                "performance_rating": self._label_or_default(rec.performance_rating, "Average"),
            }

            try:
                _logger.info("Payload sent to FastAPI: %s", payload)
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    raw = resp.json().get("prediction", "undefined").lower()
                    risk = raw if raw in valid_keys else 'undefined'
                else:
                    risk = 'undefined'
            except Exception as e:
                _logger.error("API Error for %s: %s", rec.name, e)
                risk = 'undefined'

                # 1) Met à jour l’employé
            rec.predicted_risk = risk

            # 2) Met à jour la dernière ligne de l’historique
            last_hist = rec.historic_detaill and rec.historic_detaill.sorted(
                key=lambda h: h.date or h.create_date, reverse=True
            )[0]
            if last_hist:
                vals = {
                    'pred_risk': risk,
                    'performance': rec.performance_rating or False,
                }
                last_hist.sudo().write(vals)

        return True

    # ==================================================================
    # mapping
    # ------------------------------------------------------------------
    def _map_certificate_to_level(self, cert):
        return {
            'graduate': "Associate Degree",
            'bachelor': "Bachelor’s Degree",
            'master': "Master’s Degree",
            'doctor': "PhD",
        }.get(cert.lower(), "High School") if cert else "High School"

    def _get_company_size_label(self, size):
        return "Small" if size <= 50 else "Medium" if size <= 250 else "Large"

    def _label_or_default(self, value, default):
        """
        Convertit un code stocké (low/medium/high…) en label lisible par l’API.
        """
        return {
            "low": "Low", "medium": "Medium", "high": "High", "very_high": "Very High",
            "poor": "Poor", "fair": "Fair", "good": "Good", "excellent": "Excellent",
            "below_average": "Below Average", "yes": "Yes", "no": "No",
            "male": "Male", "female": "Female"
        }.get(value and value.lower(), default)


class HistoricEvaluation(models.Model):
    _name = 'historique.evaluation'
    _description = 'Evaluation History'

    name = fields.Char(string="Référence")
    date = fields.Datetime(string="Date de réponse", readonly=True)
    job_satis = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('very_high', 'Very High'),
        ],
        string="Job Satisfaction",
        store=True,
    )
    work_life = fields.Selection(
        [
            ('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('excellent', 'Excellent')
        ],
        string="Work-Life Balance"
    )
    performance = fields.Selection(
        [('low', 'Low'), ('below_average', 'Below Average'),
         ('average', 'Average'), ('high', 'High')],
        string="Performance Rating"
    )
    leadership_opport = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Leadership Opportunities"
    )
    innovation_opport = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Innovation Opportunities"
    )
    company_reput = fields.Selection(
        [('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('excellent', 'Excellent')],
        string="Company Reputation"
    )
    employee_recog = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('very_high', 'Very High')],
        string="Employee Recognition"
    )

    #  Risque prédit via FastAPI
    pred_risk = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('undefined', 'Undefined')],
        string="Predicted Risk", readonly=True
    )
    historic_id = fields.Many2one('hr.employee', string="Employe")
