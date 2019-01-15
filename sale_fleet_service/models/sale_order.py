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

    @api.depends('amount_untaxed', 'currency_id', 'currency_agreed_rate')
    def _compute_low_fleet_flag(self):
        for rec in self:
            if not rec.amount_untaxed:
                rec.low_fleet_flag = False
                return True
            fleet_product = self.env.ref(
                'sale_fleet_service.product_product_fleet_service')
            fleet_sol = self.order_line.filtered(
                lambda l: l.product_id == fleet_product)
            if rec.currency_agreed_rate > 1:
                amount_untaxed = round(
                    (rec.amount_untaxed - fleet_sol.price_subtotal) *
                    rec.currency_agreed_rate, 2)
            else:
                amount_untaxed = self.currency_id._convert(
                    rec.amount_untaxed, self.company_id.currency_id,
                    self.company_id, self.date_order)
            # Compute the fleet amount and validate if the fleet price
            # is lower than the price defined on the config
            fleet_price = round(amount_untaxed * .08, 2)
            if fleet_price < rec.company_id.sale_lower_total:
                rec.low_fleet_flag = True
            return True

    @api.onchange('order_line', 'currency_agreed_rate')
    def _onchange_amount_untaxed_fleet_service(self):
        if not self.amount_untaxed:
            return {}
        create_method = self.order_line.new
        if isinstance(self.id, int):
            create_method = self.order_line.create
        fleet_product = self.env.ref(
            'sale_fleet_service.product_product_fleet_service')
        fleet_sol = self.order_line.filtered(
            lambda l: l.product_id == fleet_product)
        if self.currency_agreed_rate > 1:
            amount_untaxed = round(
                (self.amount_untaxed - fleet_sol.price_subtotal) *
                self.currency_agreed_rate, 2)
        else:
            amount_untaxed = self.company_id.currency_id._convert(
                (self.amount_untaxed - fleet_sol.price_subtotal),
                self.currency_id, self.company_id, self.date_order)
        fleet_price = round(amount_untaxed * 0.08, 2)
        if fleet_price < self.company_id.sale_lower_total:
            fleet_price = self.company_id.sale_lower_total
        fleet_price = self.company_id.currency_id._convert(
            fleet_price, self.currency_id,
            self.company_id, self.date_order)
        if not fleet_sol:
            create_method({
                'product_id': fleet_product.id,
                'product_uom_qty': 1,
                'name': fleet_product.display_name,
                'price_unit': fleet_price,
                'order_id': self.id,
                'product_uom': fleet_product.uom_id.id,
                'iho_price_list': fleet_price,
                'iho_factor': 1,
            })
            return {}
        fleet_sol.update({
            'price_unit': fleet_price,
            'iho_price_list': fleet_price,
            'iho_factor': 1,
        })
        return {}
