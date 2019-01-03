from odoo import models, fields, api
from datetime import datetime


class JobsDashboard(models.Model):
    _name = 'jobs.dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.depends('award_date','end_date')
    def _compute_duration(self):
        """

        :return:
        """
        if self.end_date and self.award_date:
            date = datetime.strptime(self.end_date, "%Y-%m-%d") - datetime.strptime(self.award_date, "%Y-%m-%d")
            self.project_duration = date.days

    @api.depends('job_summary_line.certified')
    def _compute_all(self):
        """

        :return:
        """
        for job in self:
            expense = 0
            progress = 0
            committed = 0
            budget = 0
            for line in job.job_summary_line:
                expense = expense + line.certified
                committed = committed + line.committed
                budget = budget + line.Budget
            job.expense = expense
            job.expense_progress = 0
            job.expense_committed = committed
            job.expense_budget = budget

    @api.depends('claim_budget')
    def _compute_claim(self):
        """

        :return:
        """
        for job in self:
            claim_to_date = 0
            committed = 0
            for order in job.sale_orders:
                committed = committed + order.amount_total
                for invoice in order.invoice_ids:
                    if invoice.state == 'paid':
                        claim_to_date = claim_to_date + invoice.amount_total
            job.claim_committed = committed
            job.claim_to_date = claim_to_date
            if job.claim_budget:
                job.claim_progress = (job.claim_to_date / job.claim_budget) * 100

    @api.depends('claim_budget','claim_to_date','claim_committed','expense','expense_budget','expense_committed')
    def _compute_profit(self):
        """

        :return:
        """
        for job in self:
            job.profit_certified = job.claim_to_date - job.expense
            job.profit_committed = job.claim_committed - job.expense_committed
            job.profit_budget = job.claim_budget - job.expense_budget
            if job.profit_budget:
                job.profit_to_date = (job.profit_certified / job.profit_budget) * 100

    @api.model
    def _compute_safety_incidents(self):
        """

        :return:
        """
        for job in self:
            job.safety_incidents = len(self.env['jobs.incident.report'].search([("job_code","=",job.id )]))

    name = fields.Char(string='Job Code', default='New')
    project_description = fields.Char(string="Project Description")
    delivery_address = fields.Char(string="Delivery Address")
    project_type = fields.Char(string="Project Type")

    sale_orders = fields.Many2many('sale.order', string='Sale Order')
    award_date = fields.Date(string='Award Date')
    end_date = fields.Date(string="End Date")
    customer_id = fields.Many2one('res.partner', string='Customer')
    project_manager = fields.Many2one('res.users', string="Project Manager")

    status = fields.Selection([('live', 'Live')])
    project_duration = fields.Integer(string="Project Duration(days)", compute=_compute_duration, readonly=True)
    profit_to_date = fields.Integer(string="Profit to Date", readonly=True)
    man_days_worked = fields.Integer(string="Man Days Worked")
    safety_incidents = fields.Integer(string="Safety Incident",compute=_compute_safety_incidents)
    last_payment_date = fields.Date(string="Last Payment Day")

    job_summary_line = fields.One2many('job.summary.line', 'job_id', string='Job Summary Line', copy=True, auto_join=True)
    expense = fields.Integer(string="Expenses", compute =_compute_all, readonly=True)
    expense_progress = fields.Integer(string="Progress", compute=_compute_all, readonly=True)
    expense_committed = fields.Integer(string="Committed", compute=_compute_all, readonly=True)
    expense_budget = fields.Integer(string="Budget", compute=_compute_all, readonly=True)

    claim_to_date = fields.Integer(string="Claim to Date", compute=_compute_claim, readonly=True)
    claim_progress = fields.Integer(string="Progress", compute=_compute_claim, readonly=True)
    claim_committed = fields.Integer(string="Committed", compute=_compute_claim, readonly=True)
    claim_budget = fields.Integer(string="Budget")

    profit_certified = fields.Integer(compute=_compute_profit, readonly=True)
    profit_committed = fields.Integer(compute=_compute_profit, readonly=True)
    profit_budget = fields.Integer(compute=_compute_profit,readonly=True)

    advance_payment_bond = fields.Integer(string="Advance Payment Bond(%)")
    performance_bond = fields.Integer(string="Performance Bond(%)")
    dlp_duration = fields.Integer(string="DLP Duration(Mth)")
    ld_max = fields.Integer(string="LD Max")
    ld_rate = fields.Integer(string="LD Rate")
    consequence_damages = fields.Boolean(string="Consequential Damages")
    retention = fields.Integer(string="Retention")
    confirmation_date = fields.Date(string="Confirmation Date")
    contract_value = fields.Integer(string="Contract Value")
    currency_id = fields.Many2one("res.currency", string="Currency")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.code')
        return super(JobsDashboard, self).create(vals)

    @api.model
    @api.onchange("sale_orders")
    def onchange_saleorder(self):
        """

        :return:
        """
        if self.sale_orders:
            sale_order = self.sale_orders[0]
            self.customer_id = sale_order.partner_id
            self.delivery_address = sale_order.partner_id.contact_address
            self.confirmation_date = sale_order.confirmation_date
            self.currency_id = sale_order.currency_id
            amount = 0
            for order in self.sale_orders:
                amount = amount + order.amount_total
            self.contract_value = amount


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    job_id = fields.Many2one('jobs.dashboard', string="Job Code")


class JobSummaryLines(models.Model):
    _name = 'job.summary.line'

    @api.depends('category_id','Budget')
    def _compute_values(self):
        """

        :return:
        """
        for line in self:
            if line.category_id:
                commit_amount = 0
                certified_amount = 0
                purchase_orders = self.env['purchase.order'].search([("job_id.name", "=", line.job_id.name),("state",'=',"purchase")])
                for order in purchase_orders:
                    order_lines = order.order_line
                    for ol in order_lines:
                        if ol.product_id.categ_id.id == line.category_id.id:
                            commit_amount = commit_amount + ol.price_subtotal
                            certified_amount = certified_amount + (ol.qty_invoiced * ol.price_unit)
                line.certified = certified_amount
                line.committed = commit_amount
                if line.Budget:
                    line.progress = (line.certified / line.Budget) * 100

    job_id = fields.Many2one('jobs.dashboard', string='Job Reference', required=True, ondelete='cascade', index=True, copy=False)
    category_id = fields.Many2one('product.category', string='Expense Category', required=True)
    certified = fields.Integer(string="Certified", compute=_compute_values, readonly=True)
    progress = fields.Integer(string="Progress",compute=_compute_values, readonly=True)
    committed = fields.Integer(string="Committed", compute=_compute_values, readonly=True)
    Budget = fields.Integer(string="Budget")

