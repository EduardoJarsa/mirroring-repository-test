# Copyright 2019, 2020, MTNET Services, S.A. de C.V.
# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.lead"

    employee_ids = fields.One2many(
        "crm.team.definition",
        "lead_id",
        ondelete="set null",
        delegate=True,
        help="This is the identifier for the employee",
    )

    total_percentage = fields.Integer(String="Total Percentage", compute="_compute_total_percentage")

    @api.depends("employee_ids")
    def _compute_total_percentage(self):
        total_percentage = 0
        for team_member in self.employee_ids:
            total_percentage += team_member.percentage
        self.total_percentage = total_percentage

    @api.constrains("employee_ids")
    def _validate_total_percentage(self):
        self.invalidate_cache()
        total_percentage = 0
        for team_member in self.employee_ids:
            total_percentage += team_member.percentage
        if total_percentage != 100:
            raise ValidationError(_("Total percentage is not 100: [%i]") % total_percentage)

    @api.model
    def create(self, vals):
        if self.user_id:
            team_member_id = self.env["hr.employee"].search([("user_id", "=", self.user_id.id)]).id
            vals["employee_ids"] = [
                (
                    0,
                    0,
                    {
                        "team_member_id": team_member_id,
                        "percentage": 100,
                    },
                )
            ]
        new_record = super().create(vals)
        return new_record
