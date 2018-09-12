# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestSaleOrder(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_id = self.env.ref('product.product_product_10')
        self.product_id_2 = self.env.ref('product.product_product_11')
        self.product_fleet = self.env.ref(
            'sale_fleet_service.product_product_fleet_service')
        self.customer = self.env.ref('base.res_partner_10')
        self.company_currency = self.env.user.company_id.currency_id
        self.env.user.company_id.sale_lower_total = 150
        self.sale_lower_total = (
            self.env.user.company_id.sale_lower_total)

    def create_sale_order(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'currency_id': self.company_currency.id,
        })
        sale_order.order_line.create({
            'product_id': self.product_id.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
            'price_unit': 100,
            'name': self.product_id.display_name,
            'order_id': sale_order.id,
        })
        return sale_order

    def get_fleet_sol(self, order):
        return order.order_line.filtered(
            lambda l: l.product_id == self.product_fleet)

    def get_fleet_price(self, order):
        fleet_price = round(order.amount_total * 0.08, 2)
        if fleet_price < self.sale_lower_total:
            fleet_price = self.sale_lower_total
        return fleet_price

    def test_001_compute_low_fleet_flag(self):
        sale_order = self.create_sale_order()
        sale_order._compute_low_fleet_flag()
        self.assertTrue(sale_order.low_fleet_flag)

    def test_002_sale_order_onchange_amount_total_fleet_service(self):
        # New Sale Order Test
        sale_order = self.create_sale_order()
        fleet_price = self.get_fleet_price(sale_order)
        sale_order._onchange_amount_total_fleet_service()
        fleet_sol = self.get_fleet_sol(sale_order)
        self.assertEqual(
            fleet_sol.price_subtotal, fleet_price)

        # Fleet Line Update Test
        sale_order.order_line.create({
            'product_id': self.product_id_2.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
            'price_unit': 4000,
            'name': self.product_id.display_name,
            'order_id': sale_order.id,
        })
        fleet_price = self.get_fleet_price(sale_order)
        sale_order._onchange_amount_total_fleet_service()
        fleet_sol = self.get_fleet_sol(sale_order)
        self.assertEqual(
            fleet_sol.price_subtotal, fleet_price)

        # No amount total test
        sale_order.order_line.unlink()
        sale_order._onchange_amount_total_fleet_service()
        fleet_sol = self.get_fleet_sol(sale_order)
        self.assertFalse(fleet_sol)
