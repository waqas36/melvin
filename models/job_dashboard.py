from odoo import models, fields, api


class JobsDashboard(models.Model):
    _name = 'jobs.dashboard'

    name = fields.Char(string='Job Code', default='New')
    project_description = fields.Char(string='Project Description')
    customer = fields.Char(string="", compute='_compute_complete_name')
    sale_order_id = fields.Many2many('sale.order', string='Sale Order')
    award_date = fields.Date(string='Award Date')
    end_date = fields.Date(string="End Date")
    customer_id = fields.Many2one('res.partner', string='Customer')
    project_manager = fields.Char(string='Project Manager')
    total = fields.Integer(string="Total")
    status = fields.Selection([('live', 'Live')], default='live', readonly=True)
    state = fields.Selection([('dispute', 'Dispute'), ('incident', 'Incident'), ('live', 'Live')], string='State',
                             default='dispute')
    green_color = fields.Boolean(default=False)
    orange_color = fields.Boolean(default=False)
    red_color = fields.Boolean(default=True)

    @api.depends('name')
    def _compute_complete_name(self):
        sale_obj = self.env['sale.order'].search([()])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.code')
        return super(JobsDashboard, self).create(vals)

    @api.multi
    def action_dispute(self):
        self.state = 'incident'
        self.red_color = False
        self.orange_color = True

    @api.multi
    def action_incident(self):
        self.state = 'live'
        self.orange_color = False
        self.green_color = True


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_id = fields.Many2one('jobs.dashboard', string="Job Code")
