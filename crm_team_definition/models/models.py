
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
            raise ValidationError(_('The total '
                                    'percentage must be '
                                    'equal to 100%, '
                                    'please '
                                    'reorganize'))

    @api.model
    def create(self, vals):
        new_record = super().create(vals)
        self.env['crm.team.definition'].create(
            {'name': new_record.id,
             'team_member':
                 self.env['hr.employee'].search([('crm.lead.user_id',
                                                  '=',
                                                  self.env.uid)]).id,
             'percentage': 100})
        return new_record


class CrmTeamDefMember(models.Model):

    _name = 'crm.team.definition'
    _parent_name = 'name'
    name = fields.Integer(string='Lead Id:',
                          readonly=True,
                          visible=False)
    team_member = fields.Many2one('hr.employee',
                                  'Team Member:',
                                  required=False)
    percentage = fields.Integer(string="Percentage:",
                                required=True)

    _sql_constraints = [('team_member_unique',
                         'unique(team_member, name)',
                         'Team members must be unique')]

    @api.onchange('percentage')
    def __verify_percentage(self):
        if self.percentage > 100.00 or self.percentage < 0.00:
            raise ValidationError(_('Percentage '
                                    'must lesser or '
                                    'equal than '
                                    '100 percent or '
                                    'greater '
                                    'than zero'))

    oppor_percentage = fields.Float(digits=(6, 2),
                                    string='Opportunity Percentage',
                                    compute='_compute_opportunity_'
                                            'percentage')

    @api.multi
    @api.depends('percentage')
    def _compute_opportunity_percentage(self):
        self.ensure_one()
        for record in self:
            record.oppor_percentage = \
                record.env['crm.lead'].browse(record.name)\
                .planned_revenue * (record.percentage/100)
