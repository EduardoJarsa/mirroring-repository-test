# Copyright 2019, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("team_id")
    def _onchange_crm_team_set_analytic_tags(self):
        self.analytic_tag_ids = self.team_id.analytic_tag_ids.ids
