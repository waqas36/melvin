from odoo import models, fields


class JobsDashboard(models.Model):
    _name = 'jobs.dashboard'

    name = fields.Char(string='Project Code')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    award_date = fields.Date(string='Award Date')
    end_date = fields.Date(string="End Date")
    customer_id = fields.Many2one('res.partner', string='Customer')
    project_manager = fields.Char(string='Project Manager')
    total = fields.Integer(string="Total")
    status = fields.Selection([('live', 'Live')])

