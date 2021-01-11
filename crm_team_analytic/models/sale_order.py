# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# Copyright 2021, mtnet Services, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('team_id')
    def _onchange_crm_team_set_analytic_tags(self):
        self.analytic_tag_ids = self.team_id.analytic_tag_ids.ids

    @api.constrains('analytic_tag_ids')
    def _validate_analytic_tag_ids_team_tags(self):
        if self.analytic_tag_ids.ids == []:
            self.analytic_tag_ids = self.team_id.analytic_tag_ids.ids
