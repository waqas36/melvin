from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "account.invoice"

    project_code = fields.Char(string='Project Code', compute='_get_project_code')

    @api.depends('origin')
    def _get_project_code(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        self.project_code = sale_obj.job_dashboard_id.name
