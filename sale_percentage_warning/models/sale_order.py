# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    max_percentage = fields.Boolean(
        compute="_compute_max_percentage",
    )

    @api.depends('order_line.discount')
    def _compute_max_percentage(self):
        discounts = self.order_line.mapped('discount')
        max_percentage = self.company_id.max_percentage
        if any(discount > max_percentage for discount in discounts):
            self.max_percentage = True
