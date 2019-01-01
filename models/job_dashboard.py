from odoo import models, fields, api


class JobsDashboard(models.Model):
    _name = 'jobs.dashboard'

    name = fields.Char(string='Job Code', default='New')
    sale_order_id = fields.Many2many('sale.order', string='Sale Order')
    award_date = fields.Date(string='Award Date')
    end_date = fields.Date(string="End Date")
    customer_id = fields.Many2one('res.partner', string='Customer')
    project_manager = fields.Char(string='Project Manager')
    total = fields.Integer(string="Total")
    status = fields.Selection([('live', 'Live')])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.code')
        return super(JobsDashboard, self).create(vals)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_id = fields.Many2one('jobs.dashboard', string="Job Code")
