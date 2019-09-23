
from odoo.exceptions import ValidationError
from odoo import _, api, fields, models


class CrmTeamDefMember(models.Model):

    _name = 'crm.team.definition'
    _parent_name = 'name'
    name = fields.Integer(string='Lead Id:',
                          readonly=True,
                          visible=False)
    team_member_id = fields.Many2one('hr.employee',
                                     'Team Member:',
                                     required=True)
    percentage = fields.Integer(string="Percentage:",
                                required=True)

    _sql_constraints = [('team_member_unique',
                         'unique(team_member_id, name)',
                         'Team members must be unique')]

    @api.onchange('percentage')
    def _verify_percentage(self):
        if self.percentage > 100.00 or self.percentage < 0.00:
            raise ValidationError(_(
                'Percentage must lesser or equal than 100 '
                'percent or greater than zero'))

    oppor_percentage = fields.Float(string='Opportunity Percentage',
                                    digits=(6, 2),
                                    compute='_compute_opportunity_'
                                            'percentage')

    @api.multi
    @api.depends('percentage')
    def _compute_opportunity_percentage(self):
        for record in self:
            record.oppor_percentage = \
                record.env['crm.lead'].browse(record.name)\
                .planned_revenue * (record.percentage/100)
