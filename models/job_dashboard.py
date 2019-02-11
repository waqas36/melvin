from datetime import datetime

from odoo import models, fields, api


class JobsDashboard(models.Model):
    _name = 'jobs.dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.depends('award_date', 'end_date')
    def _compute_duration(self):
        """

        :return:
        """
        if self.end_date and self.award_date:
            date = datetime.strptime(self.end_date, "%Y-%m-%d") - datetime.strptime(self.award_date, "%Y-%m-%d")
            self.project_duration = date.days

    @api.depends('sale_orders')
    def _get_last_date(self):
        """

        :return:
        """
        payment_date_list = []
        for order in self.env['sale.order'].search([]):
            for invoice in order.invoice_ids:
                payments = self.env['account.payment'].search([('communication', '=', invoice.number)])
                if payments:
                    payment_date_list.append(payments[0].payment_date)
        if payment_date_list:
            self.last_payment_date = max(payment_date_list)

    @api.depends('job_summary_line.certified', 'expense_budget')
    def _compute_all(self):
        """

        :return:
        """
        for job in self:
            purchase_orders = self.env["purchase.order"].search([("job_id", '=', job.id),('state', 'in', ['purchase', 'done'])])
            if purchase_orders:
                expense = 0
                committed = 0
                for po in purchase_orders:
                    committed = committed + po.amount_total
                    for vendor_bill in po.invoice_ids:
                        if vendor_bill.state == "paid":
                            expense = expense + vendor_bill.amount_total
                job.expense = expense
                job.expense_committed = committed
            if job.expense_budget:
                job.expense_progress =(job.expense / job.expense_budget) * 100

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

    @api.depends('claim_budget', 'claim_to_date', 'claim_committed', 'expense', 'expense_budget', 'expense_committed')
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
            job.safety_incidents = len(self.env['jobs.incident.report'].search([("job_code", "=", job.id)]))

    @api.multi
    def _work_hours(self):
        """

        :return:
        """
        for job in self:
            worked_hours = 0
            time_sheets = self.env["account.analytic.line"].search([("job_id", "=", job.id)])
            for sheet in time_sheets:
                worked_hours = worked_hours + sheet.hour_worked
            job.man_days_worked = worked_hours

    payment_terms = fields.Text('Payment Terms')
    notes = fields.Text('Notes')
    name = fields.Char(string='Job Code', default='New')
    project_description = fields.Text(string="Job Description")
    delivery_address = fields.Char(string="Delivery Address")
    project_type = fields.Many2one('create.project.type', string="Project Type")

    sale_orders = fields.One2many('sale.order', 'job_dashboard_id', string='Sale Order')
    award_date = fields.Date(string='Confirmation Date')
    end_date = fields.Date(string="End Date")
    customer_id = fields.Many2one('res.partner', string='Customer')
    project_manager = fields.Many2one('res.users', string="Project Manager")
    contract_type = fields.Many2one('create.contract.type', string="Contract Type")

    project_duration = fields.Integer(string="Project Duration(days)", compute=_compute_duration, readonly=True)
    profit_to_date = fields.Integer(string="Profit to Date", readonly=True)
    man_days_worked = fields.Integer(string="Work Hours",readonly=True,compute=_work_hours)
    safety_incidents = fields.Integer(string="Safety Incident", compute=_compute_safety_incidents)
    last_payment_date = fields.Date(string="Last Payment Day",compute=_get_last_date)

    job_summary_line = fields.One2many('job.summary.line', 'job_id', string='Job Summary Line', copy=True,
                                       auto_join=True)
    expense = fields.Integer(string="Cost of Sales", compute=_compute_all, readonly=True)
    expense_progress = fields.Integer(string="Work Progress :", compute=_compute_all, readonly=True)
    expense_committed = fields.Integer(string="Committed", compute=_compute_all, readonly=True)
    expense_budget = fields.Integer(string="Budget",)

    claim_to_date = fields.Integer(string="Claim to Date", compute=_compute_claim, readonly=True)
    claim_progress = fields.Integer(string="Claim Progress :", compute=_compute_claim, readonly=True)
    claim_committed = fields.Integer(string="Committed", compute=_compute_claim, readonly=True)
    claim_budget = fields.Integer(string="Budget")

    profit_certified = fields.Integer(compute=_compute_profit, readonly=True)
    profit_committed = fields.Integer(compute=_compute_profit, readonly=True)
    profit_budget = fields.Integer(compute=_compute_profit, readonly=True)

    advance_payment_bond = fields.Integer(string="Advance Payment Bond(%)")
    performance_bond = fields.Integer(string="Performance Bond(%)")
    dlp_duration = fields.Integer(string="DLP Duration(Mth)")
    ld_max = fields.Integer(string="LD Max")
    ld_rate = fields.Char(string="LD Rate")
    consequence_damages = fields.Boolean(string="Consequential Damages")
    retention = fields.Integer(string="Retention")
    confirmation_date = fields.Date(string="Confirmation Date")
    contract_value = fields.Integer(string="Contract Value")
    currency_id = fields.Many2one("res.currency", string="Currency")

    # sale_order_id = fields.Many2many('sale.order', string='Sale Order')

    status = fields.Selection([('dispute', 'ALERT'), ('incident', 'CLOSED'), ('live', 'LIVE')], default='live',
                              readonly=True, compute='_on_change_state')
    state = fields.Selection([ ('live', 'LIVE'),('incident', 'CLOSED'),('dispute', 'ALERT')], string='State',
                             default='live')
    black_color = fields.Boolean(default=True)
    grey_color = fields.Boolean(default=False)
    red_color = fields.Boolean(default=False)

    @api.depends('state')
    def _on_change_state(self):
        for rec in self:
            rec.status = rec.state

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
            self.sale_orders[-1].is_job = True
            sale_order = self.sale_orders[0]
            self.customer_id = sale_order.partner_id
            self.delivery_address = sale_order.partner_id.contact_address
            self.confirmation_date = sale_order.confirmation_date
            self.currency_id = sale_order.currency_id
            amount = 0
            for order in self.sale_orders:
                amount = amount + order.amount_total
            self.contract_value = amount

    @api.multi
    def action_dispute(self):
        self.state = 'incident'
        self.grey_color = True
        self.red_color = False

    @api.multi
    def action_incident(self):
        self.state = 'live'
        self.black_color = True
        self.grey_color = False

    @api.multi
    def action_back_to_dispute(self):
        self.state = 'dispute'
        self.grey_color = False
        self.red_color = True

    @api.multi
    def action_back_to_incident(self):
        self.state = 'incident'
        self.black_color = False
        self.grey_color = True


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    job_id = fields.Many2one('jobs.dashboard', string="Job Code")


class JobSummaryLines(models.Model):
    _name = 'job.summary.line'

    @api.depends('category_id', 'Budget')
    def _compute_values(self):
        """

        :return:
        """
        for line in self:
            if line.category_id:
                commit_amount = 0
                certified_amount = 0
                purchase_orders = self.env['purchase.order'].search(
                    [("job_id.name", "=", line.job_id.name), ("state", '=', "purchase")])
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

    job_id = fields.Many2one('jobs.dashboard', string='Job Reference', required=True, ondelete='cascade', index=True,
                             copy=False)
    category_id = fields.Many2one('product.category', string='Expense Details', required=True)
    certified = fields.Integer(string="Certified", compute=_compute_values, readonly=True)
    progress = fields.Integer(string="Progress", compute=_compute_values, readonly=True)
    committed = fields.Integer(string="Committed", compute=_compute_values, readonly=True)
    Budget = fields.Integer(string="Budget")


class CreateProjectType(models.Model):
    _name = 'create.project.type'

    name = fields.Char("Project Type")


class CreateContractType(models.Model):
    _name = 'create.contract.type'

    name = fields.Char("Contract Type")
