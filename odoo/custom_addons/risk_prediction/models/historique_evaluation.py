
from odoo import models, fields

class HistoricEvaluation(models.Model):
    _name = 'historique.evaluation'
    _description = 'Evaluation History'

    name = fields.Char(string="Référence")
    date = fields.Datetime(string="Response Date", readonly=True)
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
