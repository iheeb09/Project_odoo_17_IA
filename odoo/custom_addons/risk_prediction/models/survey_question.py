# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    category_ids = fields.Many2many(
        'survey.question.category',
        'survey_question_category_rel',
        'question_id', 'category_id',
        string="Categories"
    )
