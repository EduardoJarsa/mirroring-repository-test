# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    low_fleet_flag = fields.Boolean(
        copy=False,
        help="""Techical field used to determine if the cost of the fleet
        service is lower than the price configured on the
        main config.""",
    )

    @api.onchange('order_line', 'currency_agreed_rate', 'currency_id')
    def _onchange_amount_untaxed_fleet_service(self):
        self.low_fleet_flag = False
        if not self.amount_untaxed:
            return {}
        create_method = self.order_line.new
        if isinstance(self.id, int):
            create_method = self.order_line.create
        fleet_product = self.env.ref(
            'sale_fleet_service.product_product_fleet_service')
        fleet_line = self.order_line.filtered(
            lambda l: l.product_id == fleet_product)
        amount_untaxed = round(
            self.amount_untaxed - fleet_line.price_subtotal, 2)
        fleet_price = round(amount_untaxed * 0.08, 2)
        sale_lower_total = self.company_id.sale_lower_total
        if self.currency_agreed_rate == 1:
            currency = self.currency_id
            usd = self.env.ref('base.USD')
            if currency != usd:
                sale_lower_total = usd._convert(
                    sale_lower_total, currency,
                    self.company_id, self.date_order)
        elif self.currency_agreed_rate > 1:
            sale_lower_total = sale_lower_total * self.currency_agreed_rate
        if fleet_price < sale_lower_total:
            fleet_price = sale_lower_total
            self.low_fleet_flag = True
        # Divide with currency_agreed_rate to get the amount that is computed
        # by other method.
        fleet_price = fleet_price / self.currency_agreed_rate
        taxes = self.fiscal_position_id.map_tax(
            fleet_product.taxes_id, fleet_product, self.partner_id)
        if not fleet_line:
            create_method({
                'product_id': fleet_product.id,
                'product_uom_qty': 1,
                'price_unit': fleet_price,
                'name': fleet_product.display_name,
                'order_id': self.id,
                'product_uom': fleet_product.uom_id.id,
                'iho_price_list': fleet_price,
                'iho_factor': 1.0,
                'iho_tc': self.currency_agreed_rate,
                'iho_service_factor': 1.0,
                'tax_id': taxes,
                'sequence': 10000,
                'analytic_tag_ids': self.analytic_tag_ids.ids,
            })
            return {}
        fleet_line.update({
            'price_unit': fleet_price,
            'iho_price_list': fleet_price,
            'iho_tc': self.currency_agreed_rate,
            'iho_factor': 1.0,
            'iho_service_factor': 1.0,
            'sequence': 10000,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
        })
        return {}
