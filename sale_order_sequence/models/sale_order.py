# Copyright 2018, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        if vals["team_id"] and not vals.get("name"):
            team_obj = self.env["crm.team"]
            team = team_obj.browse(vals["team_id"])
            if team.sequence_id:
                vals["name"] = team.sequence_id.next_by_id()
        return super().create(vals)
