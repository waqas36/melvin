# -*- coding: utf-8 -*-
from odoo import http

# class Jobs(http.Controller):
#     @http.route('/jobs/jobs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jobs/jobs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jobs.listing', {
#             'root': '/jobs/jobs',
#             'objects': http.request.env['jobs.jobs'].search([]),
#         })

#     @http.route('/jobs/jobs/objects/<model("jobs.jobs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jobs.object', {
#             'object': obj
#         })