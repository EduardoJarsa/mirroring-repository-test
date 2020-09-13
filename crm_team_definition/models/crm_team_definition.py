# Copyright 2019, MTNET Services, S.A. de C.V.
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.exceptions import ValidationError
from odoo import _, api, fields, models


class CrmTeamDefinition(models.Model):

    _name = 'crm.team.definition'
    lead_id = fields.Integer(
        string='Lead Id:', readonly=True, visible=False)

    team_member_id = fields.Many2one(
        'hr.employee', 'Team Member:', required=True)

    percentage = fields.Integer(
        string="Percentage:", required=True)

    _sql_constraints = [(
        'team_member_unique',
        'unique(team_member_id, lead_id)',
        'Team members must be unique')]

    @api.onchange('percentage')
    def _verify_percentage(self):
        if self.percentage > 100.00 or self.percentage < 0.00:
            raise ValidationError(_(
                'Percentage must lesser or equal than 100 '
                'percent or greater than zero'))

    oppor_percentage = fields.Float(
        string='Opportunity Percentage',
        digits=(6, 2),
        compute='_compute_opportunity_percentage')

    @api.depends('percentage')
    def _compute_opportunity_percentage(self):
        for record in self:
            record.oppor_percentage = \
                record.env['crm.lead'].browse(record.lead_id)\
                .planned_revenue * (record.percentage/100)
