from odoo import models, fields, api

class SurveyQuestionCategory(models.Model):
    _name = 'survey.question.category'
    _description = "Category for Survey Questions"

    name  = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index")