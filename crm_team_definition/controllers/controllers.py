# -*- coding: utf-8 -*-
from odoo import http

# class CrmTeamDefinition(http.Controller):
#     @http.route('/crm_team_definition/crm_team_definition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_team_definition/crm_team_definition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_team_definition.listing', {
#             'root': '/crm_team_definition/crm_team_definition',
#             'objects': http.request.env['crm_team_definition.crm_team_definition'].search([]),
#         })

#     @http.route('/crm_team_definition/crm_team_definition/objects/<model("crm_team_definition.crm_team_definition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_team_definition.object', {
#             'object': obj
#         })