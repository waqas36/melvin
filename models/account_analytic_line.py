# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticLineExt(models.Model):
    _inherit = 'account.analytic.line'

    @api.depends('time_start', 'time_end')
    def _get_hours(self):
        for obj in self:
            if obj.time_start and obj.time_end:
                # time_start = datetime.datetime.strptime(str(self.time_start), '%H:%M')
                # time_end = datetime.datetime.strptime(str(self.time_end), '%H:%M')
                if obj.time_end >= obj.time_start:
                    obj.hour_worked = obj.time_end - obj.time_start
                else:
                    raise Warning(_("End Time should be greater than Start Time"))

    @api.depends('rate', 'hour_worked')
    def _get_charges(self):
        for rec in self:
            rec.charges = rec.hour_worked * rec.rate

    employee_id = fields.Many2one('hr.employee', string="Employee")
    job_id = fields.Many2one('jobs.dashboard', string='Job Code')
    charges = fields.Monetary(string="Charges to Job", compute=_get_charges, readonly=True)
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')
    rate = fields.Float(string="Rate ($/hr)")
    supervisor = fields.Char(string="Supervisor")
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    remarks = fields.Text(string="Notes")
    hour_worked = fields.Integer("Hours Worked", compute=_get_hours)
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', ondelete='restrict', index=True)
    name = fields.Char('Description',default="Timesheet")


