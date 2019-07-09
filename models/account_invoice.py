from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('origin')
    def _get_project_code(self):
        sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
        purchase_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
        if sale_obj:
            self.project_code = sale_obj.job_dashboard_id.id
        elif self.project_code_duplicate:
            self.project_code = self.project_code_duplicate.id

        if purchase_obj:
            self.project_code = purchase_obj.job_id.id

    project_code = fields.Many2one('jobs.dashboard', string='Job Code', readonly=False, compute="_get_project_code")
    project_code_duplicate = fields.Many2one('jobs.dashboard', string='Job Code Duplicate')

    @api.onchange("project_code")
    def store_value(self):
        """

        :return:
        """
        if self.project_code:
            self.project_code_duplicate = self.project_code.id