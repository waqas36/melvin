from odoo import models, fields, api


class SaleOrderExt(models.Model):
    _inherit = 'sale.order'

    @api.depends('job_dashboard_id')
    def _check(self):
        """

        :return:
        """
        self.is_job = True

    job_dashboard_id = fields.Many2one('jobs.dashboard', string="Job ID")
    is_job = fields.Boolean(_compute=_check)
