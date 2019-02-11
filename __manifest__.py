# -*- coding: utf-8 -*-
{
    'name': "Jobs",

    'summary': """
        Custom Jobs Module for Cyclect to track, monitor and manage Jobs that are ordered""",

    'description': """
        Custom Jobs module created for the purpose of tracking, managing and monitoring job orders. Adds a wizard to create a job from sales order, removed option to create product from sales order, masterlist of jobs, submenus in jobs to provide summary of job status and overview, rights management.
    """,

    'author': "Waqas",
    'website': "http://www.cyclect.com.sg",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Jobs',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management','hr_timesheet', 'purchase'],
    'qweb': ["static/src/xml/*.xml"],

    "images": [
        "static/description/job.png"
    ],
    "application": True,

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/jobs.xml',
        'views/jobs_dashboard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/account_analytic_line.xml',

        'views/sequence.xml',
        'views/purchase_order.xml',
        'views/web_tree_dynamic_colored_field.xml',
        'views/sale_order.xml',

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
