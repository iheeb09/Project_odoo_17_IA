from odoo import models, fields


class HRMatchingCV(models.Model):
    _name = "hr.matching.cv"
    _description = "Resume to be compared with the job opening"

    job_id = fields.Many2one("hr.job", string="Job", required=True , ondelete="cascade")
    name = fields.Char("CV name", required=True)
    cv_pdf = fields.Binary("PDF File", required=True, attachment=True)
