from odoo import models, fields, api


# class ConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     project_type = fields.Char(string='Project Type')
#
#     @api.multi
#     def execute(self):
#         values = {}
#         res = super(ConfigSettings, self).execute()
#         values['project_type'] = self.project_type
#         res.update({'project_type': values['project_type'] or False})
#
#         return res


class ResCompany(models.Model):
    _inherit = "res.company"

    project_type = fields.Char(string='Project Type')


class AccountConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    def _default_project_type(self):
        return self.env.user.company_id.project_type

    project_type = fields.Char(string='Project Type', related='company_id.project_type',
                               default=lambda self: self._default_project_type(),
                               required=True)

