# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAnalyticLineExt(models.Model):
    _inherit = 'account.analytic.line'

    # employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_code = fields.Char(string="Employee Code")
    job_code = fields.Char(string="Job Code")
    date = fields.Date(string="Date")
    time_start = fields.Datetime('Time Start')
    time_end = fields.Datetime('Time End')
    rate = fields.Char(string="Rate")
    supervisor = fields.Char(string="Supervisor")
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    remarks = fields.Text(string="Remarks")

