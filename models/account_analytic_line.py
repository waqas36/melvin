# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api,_


class AccountAnalyticLineExt(models.Model):
    _inherit = 'account.analytic.line'

    @api.depends('time_start', 'time_end')
    def _get_hours(self):
        if self.time_start and self.time_end:
            # time_start = datetime.datetime.strptime(str(self.time_start), '%H:%M')
            # time_end = datetime.datetime.strptime(str(self.time_end), '%H:%M')
            if self.time_end >= self.time_start:
                self.hour_worked = self.time_end - self.time_start
            else:
                raise Warning(_("End Time should be greater than Start Time"))

    employee_id = fields.Many2one('hr.employee', string="Employee")
    # employee_code = fields.Char(string="Employee Code")
    job_id = fields.Many2one('jobs.dashboard', string='Job Code')
    charges = fields.Float(string="Charges to Job")
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')
    rate = fields.Char(string="Rate ($/hr)")
    supervisor = fields.Char(string="Supervisor")
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    remarks = fields.Text(string="Remarks")
    hour_worked = fields.Integer("Hours Worked", compute=_get_hours)
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', ondelete='restrict', index=True)
    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

