from odoo import models, fields


class JobsIncindentReport(models.Model):
    _name = 'jobs.incident.report'

    name = fields.Char(string='PIC')
    job_code = fields.Many2one('jobs.dashboard', string='Job Code')
    incident_date = fields.Char(string='Incident Date')
    incident_details = fields.Text(string="Incident Details")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    severity = fields.Selection([('minor', 'Minor'), ('major', 'Major')])
    action = fields.Char(string='Action')
    status = fields.Selection([('open', 'Open'), ('closed', 'Closed')])
