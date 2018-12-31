from odoo import models, fields


class ConfigSettings(models.Model):
    _name = 'config.settings'

    project_type = fields.Char(string='Project Code')
    project_status = fields.Selection([('live', 'Live')], string="Project status")

