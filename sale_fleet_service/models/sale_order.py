# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    low_fleet_flag = fields.Boolean(
        compute="_compute_low_fleet_flag",
        copy=False,
        help="""Techical field used to determine if the cost of the fleet
        service is lower than the price configured on the
        main config.""",
    )

    @api.depends('amount_total')
    def _compute_low_fleet_flag(self):
        for rec in self:
            fleet_price = round(rec.amount_total * 0.08, 2)
            if (rec.amount_total and fleet_price <
                    rec.company_id.sale_lower_total):
                rec.low_fleet_flag = True

    @api.onchange('amount_total')
    def _onchange_amount_total_fleet_service(self):
        if not self.amount_total:
            return {}
        create_method = self.order_line.new
        if isinstance(self.id, int):
            create_method = self.order_line.create
        fleet_product = self.env.ref(
            'sale_fleet_service.product_product_fleet_service')
        fleet_sol = self.order_line.filtered(
            lambda l: l.product_id == fleet_product)
        fleet_price = round(self.amount_total * 0.08, 2)
        if fleet_price < self.company_id.sale_lower_total:
            fleet_price = self.company_id.sale_lower_total
        if not fleet_sol:
            create_method({
                'product_id': fleet_product.id,
                'product_uom_qty': 1,
                'name': fleet_product.display_name,
                'price_unit': fleet_price,
                'order_id': self.id,
                'product_uom': fleet_product.uom_id.id,
            })
            return {}
        fleet_sol.update({
            'price_unit': fleet_price,
        })
