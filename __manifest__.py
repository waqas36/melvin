# -*- coding: utf-8 -*-
{
    'name': "jobs",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management','hr_timesheet', 'purchase'],
    "images": [
        "static/description/job.png"
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_analytic_line.xml',
        'views/jobs.xml',
        'views/sequence.xml',
        'views/purchase_order.xml',
        'views/web_tree_dynamic_colored_field.xml',
        'views/sale_order.xml',
        'views/jobs_dashboard.xml',
        'views/config_settings.xml',
        'views/account_invoice.xml',
        'data/group.xml',
        'report/job_incident_report.xml',
        'report/job_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}