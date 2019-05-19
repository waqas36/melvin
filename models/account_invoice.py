from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "account.invoice"

    project_code = fields.Many2one('jobs.dashboard', string='Job Code', store=True, compute="_get_project_code", readonly=False)

    @api.one
    @api.depends('origin')
    def _get_project_code(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        purchase_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
        if sale_obj:
            self.project_code = sale_obj.job_dashboard_id.id
        elif purchase_obj:
            self.project_code = purchase_obj.job_id.id
