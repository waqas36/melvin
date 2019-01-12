# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticLineExt(models.Model):
    _inherit = 'account.analytic.line'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    # employee_code = fields.Char(string="Employee Code")
    name = fields.Many2one('jobs.dashboard', string='Job Code')
    charges = fields.Float(string="Charges to Job")
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')
    rate = fields.Char(string="Rate ($/hr)")
    supervisor = fields.Char(string="Supervisor")
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    remarks = fields.Text(string="Remarks")
    hour_worked = fields.Float("Hours Worked")
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    @api.onchange('time_end')
    def get_hours(self):
        if self.time_end > self.time_start:
            self.hour_worked = self.time_end - self.time_start
