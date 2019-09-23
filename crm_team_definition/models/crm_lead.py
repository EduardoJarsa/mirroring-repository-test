
from odoo.exceptions import ValidationError
from odoo import _, api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.lead'

    employee_ids = fields.One2many(
        'crm.team.definition', 'name',
        ondelete='set null',
        index=True,
        help="This is the identifier for the employee")

    total_percentage = fields.Integer(String="Total Percentage",
                                      compute='_compute_total_'
                                              'percentage')

    @api.depends('employee_ids')
    def _compute_total_percentage(self):
        total_percentage = 0.0
        for team_member in self.employee_ids:
            total_percentage += team_member.percentage
        self.total_percentage = total_percentage

    @api.constrains('employee_ids')
    def _validate_total_percentage(self):
        if self.total_percentage != 100:
            raise ValidationError(_(
                'The total percentage must be '
                'equal to 100%, please reorganize'))

    @api.model
    def create(self, vals):
        new_record = super().create(vals)
        if not new_record.user_id:
            team_member_id = new_record.user_id
        else:
            team_member_id = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)]).id
        self.env['crm.team.definition'].create(
            {
                'name': new_record.id,
                'team_member_id': team_member_id,
                'percentage': 100
            })
        return new_record
