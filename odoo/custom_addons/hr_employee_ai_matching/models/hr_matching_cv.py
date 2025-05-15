from odoo import models, fields


class HRMatchingCV(models.Model):
    _name = "hr.matching.cv"
    _description = "CV à comparer avec le poste"

    job_id = fields.Many2one("hr.matching.job", string="Poste", required=True, ondelete="cascade")
    name = fields.Char("CV name", required=True)
    cv_pdf = fields.Binary("PDF File", required=True, attachment=True)
