from odoo import models, fields


class HRMatchingResult(models.Model):
    _name = "hr.matching.result"
    _description = "AI Result : similarity score between CV and Job"

    job_id = fields.Many2one(
        "hr.job",
        string="Related Job",
        required=True,
        ondelete="cascade"
    )
    cv_name = fields.Char("CV Name", required=True)
    score = fields.Float("Similarity Score(%)", digits=(6, 2))
